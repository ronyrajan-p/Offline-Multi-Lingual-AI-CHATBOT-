from __future__ import annotations

"""Text wrapping and pagination helpers for small OLED displays."""

import textwrap


def wrap_text(text: str, width: int) -> list[str]:
    """Wrap text to a fixed character width."""

    lines: list[str] = []
    for paragraph in text.splitlines() or [text]:
        wrapped = textwrap.wrap(
            paragraph,
            width=width,
            break_long_words=True,
            replace_whitespace=False,
        )
        lines.extend(wrapped or [""])
    return lines


def paginate(lines: list[str], page_size: int) -> list[list[str]]:
    """Split lines into fixed-size pages."""

    if not lines:
        return [[""]]
    return [lines[index : index + page_size] for index in range(0, len(lines), page_size)]
