"""
Very small SQLite wrapper used to persist per-chat settings, warnings and locks.

Kept intentionally simple (plain sqlite3, short-lived connections) since a
moderation bot's write volume is low. If you scale to many thousands of
groups, swap this out for aiosqlite or Postgres without changing the public
functions below.
"""
import os
import sqlite3
import threading
from contextlib import contextmanager

from bot.config import DATABASE_PATH, DEFAULT_WARN_LIMIT, DEFAULT_WARN_ACTION

_lock = threading.Lock()

os.makedirs(os.path.dirname(DATABASE_PATH) or ".", exist_ok=True)


@contextmanager
def _conn():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_db():
    with _lock, _conn() as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_settings (
                chat_id INTEGER PRIMARY KEY,
                nsfw_filter INTEGER NOT NULL DEFAULT 1,
                link_filter INTEGER NOT NULL DEFAULT 1,
                auto_delete_seconds INTEGER NOT NULL DEFAULT 0,
                warn_limit INTEGER NOT NULL DEFAULT {warn_limit},
                warn_action TEXT NOT NULL DEFAULT '{warn_action}'
            )
            """.format(warn_limit=DEFAULT_WARN_LIMIT, warn_action=DEFAULT_WARN_ACTION)
        )
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS warns (
                chat_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                count INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (chat_id, user_id)
            )
            """
        )
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS locks (
                chat_id INTEGER NOT NULL,
                lock_type TEXT NOT NULL,
                PRIMARY KEY (chat_id, lock_type)
            )
            """
        )


def get_chat_settings(chat_id: int) -> dict:
    with _lock, _conn() as con:
        row = con.execute(
            "SELECT * FROM chat_settings WHERE chat_id = ?", (chat_id,)
        ).fetchone()
        if row is None:
            con.execute(
                "INSERT INTO chat_settings (chat_id) VALUES (?)", (chat_id,)
            )
            row = con.execute(
                "SELECT * FROM chat_settings WHERE chat_id = ?", (chat_id,)
            ).fetchone()
        return dict(row)


def update_chat_setting(chat_id: int, field: str, value) -> None:
    allowed = {
        "nsfw_filter",
        "link_filter",
        "auto_delete_seconds",
        "warn_limit",
        "warn_action",
    }
    if field not in allowed:
        raise ValueError(f"Cannot update unknown setting: {field}")
    get_chat_settings(chat_id)  # ensure row exists
    with _lock, _conn() as con:
        con.execute(
            f"UPDATE chat_settings SET {field} = ? WHERE chat_id = ?",
            (value, chat_id),
        )


def add_warn(chat_id: int, user_id: int) -> int:
    with _lock, _conn() as con:
        row = con.execute(
            "SELECT count FROM warns WHERE chat_id = ? AND user_id = ?",
            (chat_id, user_id),
        ).fetchone()
        if row is None:
            con.execute(
                "INSERT INTO warns (chat_id, user_id, count) VALUES (?, ?, 1)",
                (chat_id, user_id),
            )
            return 1
        new_count = row["count"] + 1
        con.execute(
            "UPDATE warns SET count = ? WHERE chat_id = ? AND user_id = ?",
            (new_count, chat_id, user_id),
        )
        return new_count


def reset_warns(chat_id: int, user_id: int) -> None:
    with _lock, _conn() as con:
        con.execute(
            "DELETE FROM warns WHERE chat_id = ? AND user_id = ?",
            (chat_id, user_id),
        )


def get_warns(chat_id: int, user_id: int) -> int:
    with _lock, _conn() as con:
        row = con.execute(
            "SELECT count FROM warns WHERE chat_id = ? AND user_id = ?",
            (chat_id, user_id),
        ).fetchone()
        return row["count"] if row else 0


def set_lock(chat_id: int, lock_type: str, enabled: bool) -> None:
    with _lock, _conn() as con:
        if enabled:
            con.execute(
                "INSERT OR IGNORE INTO locks (chat_id, lock_type) VALUES (?, ?)",
                (chat_id, lock_type),
            )
        else:
            con.execute(
                "DELETE FROM locks WHERE chat_id = ? AND lock_type = ?",
                (chat_id, lock_type),
            )


def get_locks(chat_id: int) -> set:
    with _lock, _conn() as con:
        rows = con.execute(
            "SELECT lock_type FROM locks WHERE chat_id = ?", (chat_id,)
        ).fetchall()
        return {r["lock_type"] for r in rows}
