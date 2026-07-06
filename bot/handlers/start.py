from telegram import Update
from telegram.ext import ContextTypes

HELP_TEXT = (
    "<b>God Bot - Group Guardian</b>\n\n"
    "I keep your group clean automatically:\n"
    "🚫 Detects and deletes NSFW/nude images (fully local, no external API)\n"
    "🔗 Detects and deletes links\n"
    "🕒 Auto-deletes media after a timer you set\n"
    "🔨 Bans, kicks, mutes, warns\n"
    "🔒 Locks specific message types\n\n"
    "<b>Setup (do this once per group):</b>\n"
    "1. Add me to your group\n"
    "2. Make me an admin with 'Delete messages' and 'Restrict members' permissions\n"
    "3. Use /settings to see current config\n\n"
    "<b>Config commands (admins only):</b>\n"
    "/nsfwfilter on|off — toggle nudity auto-delete\n"
    "/linkfilter on|off — toggle link auto-delete\n"
    "/setdeletetimer 30s|10m|2h|1d|off — auto-delete media after N time\n"
    "/warnlimit &lt;number&gt; — warns before auto-action\n"
    "/warnaction ban|mute — action taken at warn limit\n"
    "/lock links|media|stickers|forwards\n"
    "/unlock links|media|stickers|forwards\n"
    "/locks — list active locks\n\n"
    "<b>Moderation commands (reply to a user, admins only):</b>\n"
    "/ban /unban /kick /mute /unmute\n"
    "/warn /warns /resetwarn\n\n"
    "/settings — show all current settings for this group\n"
    "/help — show this message"
)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(HELP_TEXT)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_html(HELP_TEXT)
