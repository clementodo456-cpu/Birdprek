import os
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
from config import DATABASE_PATH, logger

class DatabaseManager:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self._ensure_dir_exists()
        self.init_db()

    def _ensure_dir_exists() -> None:
        """Create parent directory if it does not exist (e.g., /var/data)."""
        dirname = os.path.dirname(os.path.abspath(self.db_path))
        if dirname and not os.path.exists(dirname):
            try:
                os.makedirs(dirname, exist_ok=True)
                logger.info(f"Created database directory at: {dirname}")
            except Exception as e:
                logger.error(f"Could not create database directory {dirname}: {e}")

    def _get_connection(self) -> sqlite3.Connection:
        self._ensure_dir_exists()
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        """Initialize SQLite table structure."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    is_subscribed INTEGER DEFAULT 1,
                    delivery_time TEXT DEFAULT '08:00',
                    timezone TEXT DEFAULT 'UTC',
                    last_quote_id INTEGER DEFAULT -1,
                    motivations_received INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            logger.info("Database initialized successfully.")

    def add_or_update_user(self, user_id: int, username: Optional[str], first_name: Optional[str]) -> bool:
        """Register a new user or update existing user info."""
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
            exists = cursor.fetchone()

            if exists:
                cursor.execute("""
                    UPDATE users
                    SET username = ?, first_name = ?, updated_at = ?
                    WHERE user_id = ?
                """, (username, first_name, now, user_id))
            else:
                cursor.execute("""
                    INSERT INTO users (user_id, username, first_name, is_subscribed, delivery_time, timezone, created_at, updated_at)
                    VALUES (?, ?, ?, 1, '08:00', 'UTC', ?, ?)
                """, (user_id, username, first_name, now, now))
            conn.commit()
            return not exists

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Fetch user data by user_id."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_subscription(self, user_id: int, status: bool) -> None:
        """Enable or disable user daily motivation subscription."""
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        val = 1 if status else 0
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET is_subscribed = ?, updated_at = ? WHERE user_id = ?
            """, (val, now, user_id))
            conn.commit()

    def update_delivery_time(self, user_id: int, delivery_time: str) -> None:
        """Update preferred daily delivery time."""
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET delivery_time = ?, updated_at = ? WHERE user_id = ?
            """, (delivery_time, now, user_id))
            conn.commit()

    def update_timezone(self, user_id: int, timezone: str) -> None:
        """Update preferred timezone."""
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET timezone = ?, updated_at = ? WHERE user_id = ?
            """, (timezone, now, user_id))
            conn.commit()

    def record_motivation_sent(self, user_id: int, quote_id: int) -> None:
        """Track motivation sent to prevent duplicates and increment counter."""
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users
                SET last_quote_id = ?,
                    motivations_received = motivations_received + 1,
                    updated_at = ?
                WHERE user_id = ?
            """, (quote_id, now, user_id))
            conn.commit()

    def get_active_subscribers(self) -> List[Dict[str, Any]]:
        """Fetch all active subscribers for scheduler restoration."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE is_subscribed = 1")
            return [dict(row) for row in cursor.fetchall()]

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Fetch all registered users for admin broadcast."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            return [dict(row) for row in cursor.fetchall()]

    def get_stats(self) -> Tuple[int, int]:
        """Get (total_users, active_subscribers)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            total = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_subscribed = 1")
            active = cursor.fetchone()[0]
            return total, active

db = DatabaseManager()
