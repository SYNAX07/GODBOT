import logging

from telegram import Chat, Update
from telegram.ext import ContextTypes

from bot import database as db
from bot.utils.helpers import message_has_link
from bot.utils.permissions import bot_can_delete, is_user_admin

logger = logging.getLogger(__name__)

VALID_LOCK_TYPES = {"links", "media", "stickers", "forwards"}


async def lock_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _toggle_lock(update, context, enable=True)


async def unlock_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await _toggle_lock(update, context, enable=False)


async def _toggle_lock(update: Update, context: ContextTypes.DEFAULT_TYPE, enable: bool):
    if update.effective_chat.type == Chat.PRIVATE:
        await update.message.reply_text("Yeh command sirf groups mein kaam karta hai.")
        return
    if not await is_user_admin(update, context):
        await update.message.reply_text("Sirf group admins locks change kar sakte hain.")
        return
    if not context.args or context.args[0].lower() not in VALID_LOCK_TYPES:
        await update.message.reply_text(
            "Use: /lock <type> ya /unlock <type>\n"
            f"Valid types: {', '.join(sorted(VALID_LOCK_TYPES))}"
        )
        return

    lock_type = context.args[0].lower()
    db.set_lock(update.effective_chat.id, lock_type, enable)
    verb = "lock" if enable else "unlock"
    await update.message.reply_text(f"'{lock_type}' {verb} kar diya gaya.")


async def locks_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    locks = db.get_locks(update.effective_chat.id)
    if not locks:
        await update.message.reply_text("Koi lock active nahi hai.")
    else:
        await update.message.reply_text("Active locks: " + ", ".join(sorted(locks)))


async def enforce_locks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Registered as a low-priority group handler on all messages. Deletes
    messages that violate an active lock for their chat.
    """
    message = update.effective_message
    chat = update.effective_chat

    if chat.type == Chat.PRIVATE or message is None:
        return

    locks = db.get_locks(chat.id)
    if not locks:
        return

    if await is_user_admin(update, context):
        return

    violated = False

    if "links" in locks and message_has_link(message.text or message.caption or ""):
        violated = True
    if "media" in locks and (message.photo or message.video or message.document or message.audio):
        violated = True
    if "stickers" in locks and message.sticker:
        violated = True
    if "forwards" in locks and (message.forward_origin is not None):
        violated = True

    if not violated:
        return

    if not await bot_can_delete(update, context):
        return

    try:
        await message.delete()
    except Exception:
        logger.exception("Failed to delete message violating a lock")
