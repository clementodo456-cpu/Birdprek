import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram.ext import Application
from telegram.error import TelegramError, Forbidden

from config import logger
from database import db
from messages import get_random_quote, format_quote_message

scheduler = AsyncIOScheduler()

async def send_daily_motivation_job(user_id: int, app: Application) -> None:
    """Scheduled task to send daily motivation to a user."""
    user = db.get_user(user_id)
    if not user or not user["is_subscribed"]:
        logger.info(f"Skipping user {user_id} — unsubscribed or deleted.")
        return

    exclude_id = user.get("last_quote_id", -1)
    quote_id, quote = get_random_quote(exclude_id=exclude_id)
    text = format_quote_message(quote, header="☀️ <b>Your Daily Inspiration</b> ☀️")

    try:
        await app.bot.send_message(chat_id=user_id, text=text, parse_mode="HTML")
        db.record_motivation_sent(user_id, quote_id)
        logger.info(f"Daily motivation delivered successfully to user {user_id}.")
    except Forbidden:
        logger.warning(f"User {user_id} blocked the bot. Disabling subscription.")
        db.update_subscription(user_id, False)
        remove_user_daily_job(user_id)
    except TelegramError as e:
        logger.error(f"Failed to send daily motivation to {user_id}: {e}")

def schedule_user_daily_job(user_id: int, time_str: str, tz_str: str, app: Application) -> None:
    """Add or update scheduled daily job for a user."""
    try:
        hour, minute = map(int, time_str.split(":"))
        user_tz = pytz.timezone(tz_str)
        job_id = f"daily_motivation_{user_id}"

        # Ensure existing job is replaced
        scheduler.add_job(
            send_daily_motivation_job,
            trigger=CronTrigger(hour=hour, minute=minute, timezone=user_tz),
            args=[user_id, app],
            id=job_id,
            replace_existing=True
        )
        logger.info(f"Job scheduled for user {user_id} at {time_str} ({tz_str}).")
    except Exception as e:
        logger.error(f"Error scheduling job for user {user_id}: {e}")

def remove_user_daily_job(user_id: int) -> None:
    """Remove user scheduled job."""
    job_id = f"daily_motivation_{user_id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
        logger.info(f"Job {job_id} removed.")

def restore_all_scheduled_jobs(app: Application) -> None:
    """Restore all subscriber jobs from SQLite database on bot startup."""
    active_users = db.get_active_subscribers()
    count = 0
    for u in active_users:
        schedule_user_daily_job(
            user_id=u["user_id"],
            time_str=u.get("delivery_time", "08:00"),
            tz_str=u.get("timezone", "UTC"),
            app=app
        )
        count += 1
    logger.info(f"Successfully restored {count} daily motivation scheduled jobs.")
