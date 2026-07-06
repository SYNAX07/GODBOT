from telegram import Update
from telegram.ext import ContextTypes

from bot import database as db
from bot.handlers.moderation import NO_PERMS
from bot.utils.helpers import mention_html
from bot.utils.permissions import bot_can_restrict, is_user_admin


async def warn_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_admin(update, context):
        await update.message.reply_text("Sirf group admins warn de sakte hain.")
        return

    message = update.effective_message
    if not message.reply_to_message:
        await update.message.reply_text("Kisi user ke message par reply karke /warn use karo.")
        return

    target = message.reply_to_message.from_user
    chat_id = update.effective_chat.id
    settings = db.get_chat_settings(chat_id)

    count = db.add_warn(chat_id, target.id)
    limit = settings["warn_limit"]

    if count >= limit:
        db.reset_warns(chat_id, target.id)
        action = settings["warn_action"]
        if action == "ban" and await bot_can_restrict(update, context):
            await context.bot.ban_chat_member(chat_id, target.id)
            result_text = f"🔨 warn limit ({limit}) hit ho gaya, ban kar diya gaya."
        elif await bot_can_restrict(update, context):
            await context.bot.restrict_chat_member(chat_id, target.id, permissions=NO_PERMS)
            result_text = f"🔇 warn limit ({limit}) hit ho gaya, mute kar diya gaya."
        else:
            result_text = f"⚠️ warn limit ({limit}) hit ho gaya, lekin mujhe restrict permission nahi hai."
        await update.message.reply_html(
            f"{mention_html(target.id, target.first_name)} - {result_text}"
        )
    else:
        await update.message.reply_html(
            f"⚠️ {mention_html(target.id, target.first_name)} ko warn diya gaya "
            f"({count}/{limit})."
        )


async def warns_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if message.reply_to_message:
        target = message.reply_to_message.from_user
    else:
        target = update.effective_user

    chat_id = update.effective_chat.id
    count = db.get_warns(chat_id, target.id)
    limit = db.get_chat_settings(chat_id)["warn_limit"]
    await update.message.reply_html(
        f"{mention_html(target.id, target.first_name)} ke {count}/{limit} warns hain."
    )


async def reset_warn_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_admin(update, context):
        await update.message.reply_text("Sirf group admins warns reset kar sakte hain.")
        return

    message = update.effective_message
    if not message.reply_to_message:
        await update.message.reply_text("Kisi user ke message par reply karke /resetwarn use karo.")
        return

    target = message.reply_to_message.from_user
    db.reset_warns(update.effective_chat.id, target.id)
    await update.message.reply_html(
        f"✅ {mention_html(target.id, target.first_name)} ke warns reset kar diye gaye."
    )
