from __future__ import annotations

from .utils import normalize_text, truncate_text


class ResponseFormatter:
    def __init__(self, max_chars: int = 420) -> None:
        self.max_chars = max_chars

    def format(self, text: str) -> str:
        cleaned = normalize_text(text)
        return truncate_text(cleaned, self.max_chars)
