from __future__ import annotations

"""Small utility functions shared by the chatbot core."""

import re
from datetime import datetime, timezone


def utc_now_iso() -> str:
    """Return the current UTC time as an ISO-8601 string."""

    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def normalize_text(text: str) -> str:
    """Trim text and collapse repeated whitespace into single spaces."""

    return re.sub(r"\s+", " ", text.strip())


def truncate_text(text: str, limit: int) -> str:
    """Return text no longer than `limit`, using an ellipsis when truncated."""

    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)].rstrip() + "..."
