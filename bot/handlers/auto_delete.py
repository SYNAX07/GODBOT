import logging

from telegram import Chat, Update
from telegram.ext import ContextTypes

from bot import database as db

logger = logging.getLogger(__name__)


async def schedule_auto_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Registered on any media message (photo/video/document/audio/voice/
    animation/sticker) in groups. If the group has an auto-delete timer
    configured, schedules deletion of that message after the timer expires.
    """
    message = update.effective_message
    chat = update.effective_chat

    if chat.type == Chat.PRIVATE or message is None:
        return

    settings = db.get_chat_settings(chat.id)
    seconds = settings["auto_delete_seconds"]
    if seconds <= 0:
        return

    context.job_queue.run_once(
        _delete_message_job,
        when=seconds,
        data={"chat_id": chat.id, "message_id": message.message_id},
        name=f"autodelete-{chat.id}-{message.message_id}",
    )


async def _delete_message_job(context: ContextTypes.DEFAULT_TYPE):
    job_data = context.job.data
    try:
        await context.bot.delete_message(
            chat_id=job_data["chat_id"], message_id=job_data["message_id"]
        )
    except Exception:
        # Message may already be deleted / too old to delete - that's fine.
        logger.debug(
            "Could not auto-delete message %s in chat %s (already gone?)",
            job_data["message_id"],
            job_data["chat_id"],
        )
