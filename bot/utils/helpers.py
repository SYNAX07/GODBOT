import re

URL_REGEX = re.compile(
    r"(https?://\S+|www\.\S+|t\.me/\S+|telegram\.me/\S+|@[A-Za-z0-9_]{5,32}\b)",
    re.IGNORECASE,
)

TIME_UNITS = {
    "s": 1,
    "m": 60,
    "h": 3600,
    "d": 86400,
}


def message_has_link(text: str) -> bool:
    if not text:
        return False
    return bool(URL_REGEX.search(text))


def parse_duration(value: str) -> int:
    """
    Parses strings like '30s', '10m', '2h', '1d' into a number of seconds.
    Returns 0 for '0' / 'off' (meaning: disabled).
    Raises ValueError if the format is invalid.
    """
    value = value.strip().lower()
    if value in ("0", "off", "none", "disable", "disabled"):
        return 0

    match = re.fullmatch(r"(\d+)([smhd])", value)
    if not match:
        raise ValueError(
            "Invalid duration. Use formats like 30s, 10m, 2h, 1d, or 'off'."
        )
    amount, unit = match.groups()
    return int(amount) * TIME_UNITS[unit]


def format_duration(seconds: int) -> str:
    if seconds <= 0:
        return "disabled"
    for unit_name, unit_seconds in (("day", 86400), ("hour", 3600), ("minute", 60)):
        if seconds % unit_seconds == 0:
            amount = seconds // unit_seconds
            return f"{amount} {unit_name}{'s' if amount != 1 else ''}"
    return f"{seconds} seconds"


def mention_html(user_id: int, name: str) -> str:
    safe_name = (
        name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )
    return f'<a href="tg://user?id={user_id}">{safe_name}</a>'
