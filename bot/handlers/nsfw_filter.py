import logging
import os
import tempfile

from telegram import Chat, Update
from telegram.ext import ContextTypes

from bot import database as db
from bot.utils.helpers import mention_html
from bot.utils.nsfw_detector import is_image_nsfw
from bot.utils.permissions import bot_can_delete, is_user_admin

logger = logging.getLogger(__name__)


async def scan_media_for_nsfw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Registered on photo / sticker / animation messages in groups.
    Downloads the image, runs it through the local NudeNet model, and
    deletes the message (+ optionally warns the sender) if it's flagged.
    """
    message = update.effective_message
    chat = update.effective_chat

    if chat.type == Chat.PRIVATE or message is None:
        return

    settings = db.get_chat_settings(chat.id)
    if not settings["nsfw_filter"]:
        return

    # Never flag messages sent by group admins (avoids accidental self-lockout).
    if await is_user_admin(update, context):
        return

    file_id = None
    if message.photo:
        file_id = message.photo[-1].file_id
    elif message.sticker and not message.sticker.is_animated and not message.sticker.is_video:
        file_id = message.sticker.file_id
    elif message.animation:
        # Animations (GIFs) are videos under the hood; NudeNet only handles
        # static images, so we skip these for now to avoid false negatives
        # being reported as "checked".
        return

    if not file_id:
        return

    if not await bot_can_delete(update, context):
        return

    tg_file = await context.bot.get_file(file_id)
    with tempfile.TemporaryDirectory() as tmp_dir:
        local_path = os.path.join(tmp_dir, "check.jpg")
        await tg_file.download_to_drive(local_path)
        try:
            nsfw = await is_image_nsfw(local_path)
        except Exception:
            logger.exception("NSFW check crashed, allowing message through")
            return

    if nsfw:
        try:
            await message.delete()
        except Exception:
            logger.exception("Failed to delete NSFW message")
            return

        user = message.from_user
        warning = (
            f"🚫 {mention_html(user.id, user.first_name)}, aapka media hataya gaya "
            f"kyunki usme NSFW content detect hua."
        )
        await context.bot.send_message(chat.id, warning, parse_mode="HTML")
