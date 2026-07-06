import logging

from telegram import Chat, Update
from telegram.ext import ContextTypes

from bot import database as db
from bot.utils.helpers import mention_html, message_has_link
from bot.utils.permissions import bot_can_delete, is_user_admin

logger = logging.getLogger(__name__)


async def scan_message_for_links(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat = update.effective_chat

    if chat.type == Chat.PRIVATE or message is None:
        return

    settings = db.get_chat_settings(chat.id)
    if not settings["link_filter"]:
        return

    if await is_user_admin(update, context):
        return

    text = message.text or message.caption or ""
    if not message_has_link(text):
        return

    if not await bot_can_delete(update, context):
        return

    try:
        await message.delete()
    except Exception:
        logger.exception("Failed to delete message with link")
        return

    user = message.from_user
    warning = (
        f"🔗 {mention_html(user.id, user.first_name)}, links allowed nahi hain "
        f"is group mein. Message delete kar diya gaya."
    )
    await context.bot.send_message(chat.id, warning, parse_mode="HTML")
