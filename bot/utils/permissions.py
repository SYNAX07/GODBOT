"""
Helpers to check whether a user is a group admin / the bot owner, and
whether the bot itself has the rights it needs to moderate a chat.
"""
from telegram import Chat, Update
from telegram.ext import ContextTypes

from bot.config import OWNER_IDS


async def is_user_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int = None) -> bool:
    chat = update.effective_chat
    user_id = user_id or update.effective_user.id

    if user_id in OWNER_IDS:
        return True

    if chat.type == Chat.PRIVATE:
        return True

    member = await context.bot.get_chat_member(chat.id, user_id)
    return member.status in ("administrator", "creator")


async def bot_can_delete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    chat = update.effective_chat
    if chat.type == Chat.PRIVATE:
        return False
    bot_member = await context.bot.get_chat_member(chat.id, context.bot.id)
    return bool(getattr(bot_member, "can_delete_messages", False)) or bot_member.status == "creator"


async def bot_can_restrict(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    chat = update.effective_chat
    if chat.type == Chat.PRIVATE:
        return False
    bot_member = await context.bot.get_chat_member(chat.id, context.bot.id)
    return bool(getattr(bot_member, "can_restrict_members", False)) or bot_member.status == "creator"
