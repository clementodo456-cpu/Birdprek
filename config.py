import os
import logging
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Logger setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("DailyMotivationBot")

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is missing!")

try:
    ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
except ValueError:
    ADMIN_ID = 0
    logger.warning("ADMIN_ID is invalid or missing. Admin features will be disabled.")

DATABASE_PATH = os.getenv("DATABASE_PATH", "motivation_bot.db")

# Preset Options
AVAILABLE_TIMES = [
    "06:00", "07:00", "08:00", "09:00", 
    "10:00", "12:00", "15:00", "18:00", 
    "20:00", "22:00"
]

AVAILABLE_TIMEZONES = [
    "UTC",
    "US/Eastern",
    "US/Pacific",
    "Europe/London",
    "Europe/Paris",
    "Asia/Dubai",
    "Asia/Kolkata",
    "Asia/Bangkok",
    "Asia/Singapore",
    "Asia/Tokyo",
    "Australia/Sydney"
]
