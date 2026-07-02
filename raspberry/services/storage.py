from __future__ import annotations

"""SQLite persistence for sessions, messages, settings, and errors."""

import sqlite3
from pathlib import Path

from raspberry.core.utils import utc_now_iso


class SQLiteStorage:
    """Small SQLite repository for local-only device data."""

    def __init__(self, database_path: Path, schema_path: Path) -> None:
        self.database_path = database_path
        self.schema_path = schema_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

    def initialize(self) -> None:
        """Create missing database tables from the schema file."""

        with self.connect() as connection:
            connection.executescript(self.schema_path.read_text(encoding="utf-8"))

    def connect(self) -> sqlite3.Connection:
        """Open a SQLite connection with row objects enabled."""

        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def create_session(self, language: str) -> int:
        """Create a chat session and return its database id."""

        with self.connect() as connection:
            cursor = connection.execute(
                "INSERT INTO sessions(language, created_at) VALUES (?, ?)",
                (language, utc_now_iso()),
            )
            return int(cursor.lastrowid)

    def save_message(self, session_id: int, role: str, content: str) -> None:
        """Persist one user or assistant message."""

        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO messages(session_id, role, content, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (session_id, role, content, utc_now_iso()),
            )

    def save_setting(self, key: str, value: str) -> None:
        """Insert or update one device setting."""

        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO settings(key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = excluded.updated_at
                """,
                (key, value, utc_now_iso()),
            )

    def log_error(self, message: str) -> None:
        """Persist one runtime error message."""

        with self.connect() as connection:
            connection.execute(
                "INSERT INTO error_logs(message, created_at) VALUES (?, ?)",
                (message, utc_now_iso()),
            )
