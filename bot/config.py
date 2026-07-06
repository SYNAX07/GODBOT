"""
Central configuration for the bot. Loads values from environment variables
(populated from a .env file via python-dotenv).
"""
import os
from dotenv import load_dotenv

load_dotenv()


def _get_bool(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


def _get_int_list(name: str):
    val = os.getenv(name, "")
    result = []
    for part in val.split(","):
        part = part.strip()
        if part.isdigit():
            result.append(int(part))
    return result


BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
OWNER_IDS = _get_int_list("OWNER_IDS")
DEFAULT_WARN_LIMIT: int = int(os.getenv("DEFAULT_WARN_LIMIT", "3"))
DEFAULT_WARN_ACTION: str = os.getenv("DEFAULT_WARN_ACTION", "mute").lower()
NSFW_THRESHOLD: float = float(os.getenv("NSFW_THRESHOLD", "0.55"))
DATABASE_PATH: str = os.getenv("DATABASE_PATH", "data/bot.db")

if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN is not set. Copy .env.example to .env and fill in your bot token."
    )
