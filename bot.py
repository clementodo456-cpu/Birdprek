import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from telegram.error import TelegramError, Forbidden

from config import BOT_TOKEN, ADMIN_ID, AVAILABLE_TIMES, AVAILABLE_TIMEZONES, logger
from database import db
from messages import (
    get_random_quote,
    format_quote_message,
    WELCOME_TEXT,
    HELP_TEXT,
    ABOUT_TEXT
)
from scheduler import (
    scheduler,
    schedule_user_daily_job,
    remove_user_daily_job,
    restore_all_scheduled_jobs
)

# ----------------- Keyboard Markup Helpers ----------------- #

def build_main_keyboard(is_subscribed: bool) -> InlineKeyboardMarkup:
    sub_text = "🔕 Disable Daily" if is_subscribed else "🔔 Enable Daily"
    keyboard = [
        [InlineKeyboardButton("💪 Get Motivation", callback_data="cb_motivate")],
        [
            InlineKeyboardButton(sub_text, callback_data="cb_toggle_daily"),
            InlineKeyboardButton("⏰ Set Time", callback_data="cb_menu_time")
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="cb_menu_settings"),
            InlineKeyboardButton("ℹ️ Help", callback_data="cb_help")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def build_settings_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🔔 Toggle Subscription", callback_data="cb_toggle_daily")],
        [InlineKeyboardButton("⏰ Change Delivery Time", callback_data="cb_menu_time")],
        [InlineKeyboardButton("🌍 Change Timezone", callback_data="cb_menu_tz")],
        [InlineKeyboardButton("📊 My Status", callback_data="cb_status")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="cb_main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def build_times_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for t in AVAILABLE_TIMES:
        row.append(InlineKeyboardButton(t, callback_data=f"cb_set_time:{t}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("🔙 Back", callback_data="cb_menu_settings")])
    return InlineKeyboardMarkup(buttons)

def build_tz_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for tz in AVAILABLE_TIMEZONES:
        row.append(InlineKeyboardButton(tz, callback_data=f"cb_set_tz:{tz}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("🔙 Back", callback_data="cb_menu_settings")])
    return InlineKeyboardMarkup(buttons)

def build_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="cb_main_menu")]])

# ----------------- Command Handlers ----------------- #

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user:
        return

    db.add_or_update_user(user.id, user.username, user.first_name)
    user_data = db.get_user(user.id)
    is_sub = bool(user_data["is_subscribed"]) if user_data else True

    # Register default job if new subscriber
    if is_sub:
        schedule_user_daily_job(
            user.id,
            user_data.get("delivery_time", "08:00"),
            user_data.get("timezone", "UTC"),
            context.application
        )

    await update.message.reply_html(
        WELCOME_TEXT,
        reply_markup=build_main_keyboard(is_sub)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(HELP_TEXT, reply_markup=build_back_keyboard())

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(ABOUT_TEXT, reply_markup=build_back_keyboard())

async def motivate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user:
        return
    
    db.add_or_update_user(user.id, user.username, user.first_name)
    user_data = db.get_user(user.id) or {}
    exclude_id = user_data.get("last_quote_id", -1)

    quote_id, quote = get_random_quote(exclude_id=exclude_id)
    db.record_motivation_sent(user.id, quote_id)

    msg = format_quote_message(quote, header="💡 <b>Instant Motivation</b>")
    await update.message.reply_html(msg, reply_markup=build_back_keyboard())

async def daily_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user:
        return

    db.add_or_update_user(user.id, user.username, user.first_name)
    user_data = db.get_user(user.id)
    current_status = bool(user_data.get("is_subscribed", 1))
    new_status = not current_status

    db.update_subscription(user.id, new_status)

    if new_status:
        schedule_user_daily_job(
            user.id,
            user_data.get("delivery_time", "08:00"),
            user_data.get("timezone", "UTC"),
            context.application
        )
        msg = "✅ <b>Daily Motivation Enabled!</b>\nYou will receive your daily message at the scheduled time."
    else:
        remove_user_daily_job(user.id)
        msg = "🔕 <b>Daily Motivation Disabled.</b>\nYou can enable it back anytime!"

    await update.message.reply_html(msg, reply_markup=build_main_keyboard(new_status))

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user:
        return
    db.add_or_update_user(user.id, user.username, user.first_name)
    await update.message.reply_html("⚙️ <b>Settings Menu</b>\nSelect an option to customize:", reply_markup=build_settings_keyboard())

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user:
        return

    db.add_or_update_user(user.id, user.username, user.first_name)
    u = db.get_user(user.id)
    if not u:
        await update.message.reply_text("Error fetching status.")
        return

    status_str = "🟢 Enabled" if u["is_subscribed"] else "🔴 Disabled"
    msg = (
        "📊 <b>Your Subscription Status</b>\n\n"
        f"• <b>Daily Motivation:</b> {status_str}\n"
        f"• <b>Delivery Time:</b> {u['delivery_time']}\n"
        f"• <b>Timezone:</b> {u['timezone']}\n"
        f"• <b>Motivations Received:</b> {u['motivations_received']}\n"
    )
    await update.message.reply_html(msg, reply_markup=build_settings_keyboard())

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not user:
        return
    db.update_subscription(user.id, False)
    remove_user_daily_job(user.id)
    await update.message.reply_html("🛑 <b>You have unsubscribed.</b>\nUse /start to subscribe again anytime!")

# ----------------- Admin Commands ----------------- #

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_ID:
        return
    total, active = db.get_stats()
    msg = (
        "📈 <b>Bot Statistics</b>\n\n"
        f"👥 <b>Total Users:</b> {total}\n"
        f"🔔 <b>Active Subscribers:</b> {active}"
    )
    await update.message.reply_html(msg)

async def admin_users(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_ID:
        return
    users = db.get_all_users()
    if not users:
        await update.message.reply_text("No registered users.")
        return

    text = f"📋 <b>Registered Users ({len(users)}):</b>\n\n"
    for u in users[:25]:
        sub = "🟢" if u["is_subscribed"] else "🔴"
        text += f"{sub} <b>{u['first_name']}</b> (@{u['username'] or 'N/A'}) - ID: <code>{u['user_id']}</code>\n"

    if len(users) > 25:
        text += f"\n<i>...and {len(users) - 25} more.</i>"

    await update.message.reply_html(text)

async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_html("⚠️ <b>Usage:</b> <code>/broadcast Your message here</code>")
        return

    broadcast_msg = " ".join(context.args)
    users = db.get_all_users()
    success = 0
    failed = 0

    await update.message.reply_text(f"📢 Starting broadcast to {len(users)} users...")

    for u in users:
        try:
            await context.bot.send_message(
                chat_id=u["user_id"],
                text=f"📢 <b>Announcement</b>\n\n{broadcast_msg}",
                parse_mode="HTML"
            )
            success += 1
        except Exception:
            failed += 1

    await update.message.reply_html(
        f"✅ <b>Broadcast Completed!</b>\n\n"
        f"• <b>Successful:</b> {success}\n"
        f"• <b>Failed:</b> {failed}"
    )

# ----------------- Callback Query Handler ----------------- #

async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not query.data:
        return
    await query.answer()

    user = query.from_user
    db.add_or_update_user(user.id, user.username, user.first_name)
    data = query.data
    user_data = db.get_user(user.id) or {}

    if data == "cb_main_menu":
        is_sub = bool(user_data.get("is_subscribed", 1))
        await query.edit_message_text(
            WELCOME_TEXT,
            parse_mode="HTML",
            reply_markup=build_main_keyboard(is_sub)
        )

    elif data == "cb_motivate":
        exclude_id = user_data.get("last_quote_id", -1)
        quote_id, quote = get_random_quote(exclude_id=exclude_id)
        db.record_motivation_sent(user.id, quote_id)
        msg = format_quote_message(quote, header="💡 <b>Instant Motivation</b>")
        await query.edit_message_text(msg, parse_mode="HTML", reply_markup=build_back_keyboard())

    elif data == "cb_toggle_daily":
        current_status = bool(user_data.get("is_subscribed", 1))
        new_status = not current_status
        db.update_subscription(user.id, new_status)

        if new_status:
            schedule_user_daily_job(
                user.id,
                user_data.get("delivery_time", "08:00"),
                user_data.get("timezone", "UTC"),
                context.application
            )
            msg = "✅ <b>Daily Motivation Enabled!</b>\nYou will receive your daily motivation on schedule."
        else:
            remove_user_daily_job(user.id)
            msg = "🔕 <b>Daily Motivation Disabled.</b>\nYou can enable it back anytime!"

        await query.edit_message_text(msg, parse_mode="HTML", reply_markup=build_main_keyboard(new_status))

    elif data == "cb_menu_settings":
        await query.edit_message_text("⚙️ <b>Settings Menu</b>\nSelect an option to customize:", parse_mode="HTML", reply_markup=build_settings_keyboard())

    elif data == "cb_menu_time":
        await query.edit_message_text("⏰ <b>Select Preferred Delivery Time:</b>", parse_mode="HTML", reply_markup=build_times_keyboard())

    elif data.startswith("cb_set_time:"):
        selected_time = data.split(":")[1]
        db.update_delivery_time(user.id, selected_time)

        if user_data.get("is_subscribed", 1):
            schedule_user_daily_job(user.id, selected_time, user_data.get("timezone", "UTC"), context.application)

        await query.edit_message_text(
            f"✅ <b>Delivery Time Updated!</b>\nYour new daily motivation time is <b>{selected_time}</b>.",
            parse_mode="HTML",
            reply_markup=build_settings_keyboard()
        )

    elif data == "cb_menu_tz":
        await query.edit_message_text("🌍 <b>Select Your Timezone:</b>", parse_mode="HTML", reply_markup=build_tz_keyboard())

    elif data.startswith("cb_set_tz:"):
        selected_tz = data.split(":")[1]
        db.update_timezone(user.id, selected_tz)

        if user_data.get("is_subscribed", 1):
            schedule_user_daily_job(user.id, user_data.get("delivery_time", "08:00"), selected_tz, context.application)

        await query.edit_message_text(
            f"✅ <b>Timezone Updated!</b>\nYour timezone is now set to <b>{selected_tz}</b>.",
            parse_mode="HTML",
            reply_markup=build_settings_keyboard()
        )

    elif data == "cb_status":
        status_str = "🟢 Enabled" if user_data.get("is_subscribed") else "🔴 Disabled"
        msg = (
            "📊 <b>Your Subscription Status</b>\n\n"
            f"• <b>Daily Motivation:</b> {status_str}\n"
            f"• <b>Delivery Time:</b> {user_data.get('delivery_time', '08:00')}\n"
            f"• <b>Timezone:</b> {user_data.get('timezone', 'UTC')}\n"
            f"• <b>Motivations Received:</b> {user_data.get('motivations_received', 0)}\n"
        )
        await query.edit_message_text(msg, parse_mode="HTML", reply_markup=build_settings_keyboard())

    elif data == "cb_help":
        await query.edit_message_text(HELP_TEXT, parse_mode="HTML", reply_markup=build_back_keyboard())

# ----------------- Error Handler ----------------- #

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling an update:", exc_info=context.error)

# ----------------- Lifecycle Hooks ----------------- #

async def post_init(app: Application) -> None:
    """Start APScheduler inside the running event loop."""
    scheduler.start()
    restore_all_scheduled_jobs(app)
    logger.info("Scheduler started and jobs restored successfully.")

async def post_shutdown(app: Application) -> None:
    """Cleanly shut down APScheduler on application exit."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler shut down gracefully.")

# ----------------- Application Entrypoint ----------------- #

def main() -> None:
    """Initialize and run the bot."""
    logger.info("Initializing Daily Motivation Bot...")

    # Build PTB Application with lifecycle callbacks
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )

    # Register Handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about_command))
    app.add_handler(CommandHandler("motivate", motivate_command))
    app.add_handler(CommandHandler("daily", daily_command))
    app.add_handler(CommandHandler("settings", settings_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("stop", stop_command))

    # Admin Handlers
    app.add_handler(CommandHandler("stats", admin_stats))
    app.add_handler(CommandHandler("users", admin_users))
    app.add_handler(CommandHandler("broadcast", admin_broadcast))

    # Callback Query Handler
    app.add_handler(CallbackQueryHandler(handle_callback_query))

    # Global Error Handler
    app.add_error_handler(error_handler)

    logger.info("Bot is active and listening for updates...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
