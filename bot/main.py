import logging

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from bot import database as db
from bot.config import BOT_TOKEN
from bot.handlers import (
    auto_delete,
    link_filter,
    locks,
    moderation,
    nsfw_filter,
    settings,
    start,
    warns,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Media types that should trigger the auto-delete-timer feature.
AUTO_DELETE_FILTER = (
    filters.PHOTO
    | filters.VIDEO
    | filters.Document.ALL
    | filters.AUDIO
    | filters.VOICE
    | filters.ANIMATION
    | filters.Sticker.ALL
)

# Media types that go through the NSFW scanner.
NSFW_SCAN_FILTER = filters.PHOTO | filters.Sticker.ALL | filters.ANIMATION


def build_application() -> Application:
    db.init_db()

    application = Application.builder().token(BOT_TOKEN).build()

    # --- basic ---
    application.add_handler(CommandHandler("start", start.start_command))
    application.add_handler(CommandHandler("help", start.help_command))

    # --- settings ---
    application.add_handler(CommandHandler("settings", settings.settings_command))
    application.add_handler(CommandHandler("nsfwfilter", settings.nsfw_filter_command))
    application.add_handler(CommandHandler("linkfilter", settings.link_filter_command))
    application.add_handler(CommandHandler("setdeletetimer", settings.set_delete_timer_command))
    application.add_handler(CommandHandler("warnlimit", settings.warn_limit_command))
    application.add_handler(CommandHandler("warnaction", settings.warn_action_command))

    # --- moderation commands ---
    application.add_handler(CommandHandler("ban", moderation.ban_command))
    application.add_handler(CommandHandler("unban", moderation.unban_command))
    application.add_handler(CommandHandler("kick", moderation.kick_command))
    application.add_handler(CommandHandler("mute", moderation.mute_command))
    application.add_handler(CommandHandler("unmute", moderation.unmute_command))

    # --- warns ---
    application.add_handler(CommandHandler("warn", warns.warn_command))
    application.add_handler(CommandHandler("warns", warns.warns_command))
    application.add_handler(CommandHandler("resetwarn", warns.reset_warn_command))

    # --- locks ---
    application.add_handler(CommandHandler("lock", locks.lock_command))
    application.add_handler(CommandHandler("unlock", locks.unlock_command))
    application.add_handler(CommandHandler("locks", locks.locks_command))

    # --- passive content scanners (group = order matters, run before locks) ---
    application.add_handler(
        MessageHandler(NSFW_SCAN_FILTER & filters.ChatType.GROUPS, nsfw_filter.scan_media_for_nsfw),
        group=0,
    )
    application.add_handler(
        MessageHandler(filters.TEXT & filters.ChatType.GROUPS, link_filter.scan_message_for_links),
        group=0,
    )
    application.add_handler(
        MessageHandler(filters.ChatType.GROUPS & filters.ALL, locks.enforce_locks),
        group=1,
    )
    application.add_handler(
        MessageHandler(AUTO_DELETE_FILTER & filters.ChatType.GROUPS, auto_delete.schedule_auto_delete),
        group=2,
    )

    return application


def main():
    application = build_application()
    logger.info("Bot starting (polling mode)...")
    application.run_polling(allowed_updates=["message", "chat_member"])


if __name__ == "__main__":
    main()
