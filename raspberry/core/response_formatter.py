from __future__ import annotations

"""Response cleanup for OLED display constraints."""

from .utils import normalize_text, truncate_text


class ResponseFormatter:
    """Normalize and bound assistant responses before display."""

    def __init__(self, max_chars: int = 420) -> None:
        self.max_chars = max_chars

    def format(self, text: str) -> str:
        """Return display-safe response text."""

        cleaned = normalize_text(text)
        return truncate_text(cleaned, self.max_chars)
