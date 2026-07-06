from telegram import ChatPermissions, Update
from telegram.ext import ContextTypes

from bot.utils.helpers import mention_html
from bot.utils.permissions import bot_can_restrict, is_user_admin

NO_PERMS = ChatPermissions(
    can_send_messages=False,
    can_send_audios=False,
    can_send_documents=False,
    can_send_photos=False,
    can_send_videos=False,
    can_send_video_notes=False,
    can_send_voice_notes=False,
    can_send_polls=False,
    can_send_other_messages=False,
    can_add_web_page_previews=False,
)

FULL_PERMS = ChatPermissions(
    can_send_messages=True,
    can_send_audios=True,
    can_send_documents=True,
    can_send_photos=True,
    can_send_videos=True,
    can_send_video_notes=True,
    can_send_voice_notes=True,
    can_send_polls=True,
    can_send_other_messages=True,
    can_add_web_page_previews=True,
)


async def _get_target_user(update: Update):
    message = update.effective_message
    if message.reply_to_message:
        return message.reply_to_message.from_user
    return None


async def _guard(update: Update, context: ContextTypes.DEFAULT_TYPE, need_restrict=False):
    """Shared checks: caller is admin, bot has rights, a target user was given via reply."""
    if not await is_user_admin(update, context):
        await update.message.reply_text("Sirf group admins yeh command use kar sakte hain.")
        return None

    target = await _get_target_user(update)
    if target is None:
        await update.message.reply_text(
            "Kisi user ke message par reply karke yeh command use karo."
        )
        return None

    if need_restrict and not await bot_can_restrict(update, context):
        await update.message.reply_text(
            "Mujhe 'Restrict members' / 'Ban users' permission do pehle."
        )
        return None

    return target


async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = await _guard(update, context, need_restrict=True)
    if not target:
        return
    await context.bot.ban_chat_member(update.effective_chat.id, target.id)
    await update.message.reply_html(f"🔨 {mention_html(target.id, target.first_name)} ban kar diya gaya.")


async def unban_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = await _guard(update, context, need_restrict=True)
    if not target:
        return
    await context.bot.unban_chat_member(update.effective_chat.id, target.id, only_if_banned=True)
    await update.message.reply_html(f"✅ {mention_html(target.id, target.first_name)} unban kar diya gaya.")


async def kick_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = await _guard(update, context, need_restrict=True)
    if not target:
        return
    chat_id = update.effective_chat.id
    await context.bot.ban_chat_member(chat_id, target.id)
    await context.bot.unban_chat_member(chat_id, target.id, only_if_banned=True)
    await update.message.reply_html(f"👢 {mention_html(target.id, target.first_name)} kick kar diya gaya.")


async def mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = await _guard(update, context, need_restrict=True)
    if not target:
        return
    await context.bot.restrict_chat_member(update.effective_chat.id, target.id, permissions=NO_PERMS)
    await update.message.reply_html(f"🔇 {mention_html(target.id, target.first_name)} mute kar diya gaya.")


async def unmute_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target = await _guard(update, context, need_restrict=True)
    if not target:
        return
    await context.bot.restrict_chat_member(update.effective_chat.id, target.id, permissions=FULL_PERMS)
    await update.message.reply_html(f"🔊 {mention_html(target.id, target.first_name)} unmute kar diya gaya.")
