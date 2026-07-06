from telegram import Chat, Update
from telegram.ext import ContextTypes

from bot import database as db
from bot.utils.helpers import format_duration, parse_duration
from bot.utils.permissions import is_user_admin


async def _require_group_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if update.effective_chat.type == Chat.PRIVATE:
        await update.message.reply_text("Yeh command sirf groups mein kaam karta hai.")
        return False
    if not await is_user_admin(update, context):
        await update.message.reply_text("Sirf group admins yeh setting badal sakte hain.")
        return False
    return True


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type == Chat.PRIVATE:
        await update.message.reply_text("Yeh command sirf groups mein kaam karta hai.")
        return

    s = db.get_chat_settings(chat.id)
    locks = db.get_locks(chat.id)
    text = (
        f"<b>Settings for {chat.title}</b>\n\n"
        f"NSFW filter: {'ON' if s['nsfw_filter'] else 'OFF'}\n"
        f"Link filter: {'ON' if s['link_filter'] else 'OFF'}\n"
        f"Auto-delete media after: {format_duration(s['auto_delete_seconds'])}\n"
        f"Warn limit: {s['warn_limit']}\n"
        f"Warn action: {s['warn_action']}\n"
        f"Active locks: {', '.join(sorted(locks)) if locks else 'none'}"
    )
    await update.message.reply_html(text)


async def nsfw_filter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _require_group_admin(update, context):
        return
    if not context.args or context.args[0].lower() not in ("on", "off"):
        await update.message.reply_text("Use: /nsfwfilter on  ya  /nsfwfilter off")
        return
    enabled = context.args[0].lower() == "on"
    db.update_chat_setting(update.effective_chat.id, "nsfw_filter", int(enabled))
    await update.message.reply_text(f"NSFW filter {'ON' if enabled else 'OFF'} kar diya.")


async def link_filter_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _require_group_admin(update, context):
        return
    if not context.args or context.args[0].lower() not in ("on", "off"):
        await update.message.reply_text("Use: /linkfilter on  ya  /linkfilter off")
        return
    enabled = context.args[0].lower() == "on"
    db.update_chat_setting(update.effective_chat.id, "link_filter", int(enabled))
    await update.message.reply_text(f"Link filter {'ON' if enabled else 'OFF'} kar diya.")


async def set_delete_timer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _require_group_admin(update, context):
        return
    if not context.args:
        await update.message.reply_text("Use: /setdeletetimer 30s|10m|2h|1d|off")
        return
    try:
        seconds = parse_duration(context.args[0])
    except ValueError as e:
        await update.message.reply_text(str(e))
        return
    db.update_chat_setting(update.effective_chat.id, "auto_delete_seconds", seconds)
    await update.message.reply_text(
        f"Media auto-delete timer set to: {format_duration(seconds)}"
    )


async def warn_limit_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _require_group_admin(update, context):
        return
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Use: /warnlimit <number>")
        return
    limit = max(1, int(context.args[0]))
    db.update_chat_setting(update.effective_chat.id, "warn_limit", limit)
    await update.message.reply_text(f"Warn limit set to {limit}.")


async def warn_action_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await _require_group_admin(update, context):
        return
    if not context.args or context.args[0].lower() not in ("ban", "mute"):
        await update.message.reply_text("Use: /warnaction ban|mute")
        return
    action = context.args[0].lower()
    db.update_chat_setting(update.effective_chat.id, "warn_action", action)
    await update.message.reply_text(f"Warn action set to: {action}")
