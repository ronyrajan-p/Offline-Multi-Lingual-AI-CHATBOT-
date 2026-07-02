from __future__ import annotations

"""Screen rendering utilities for small OLED displays."""

from raspberry.display.oled_driver import DisplayDriver
from raspberry.display.screens import Screen
from raspberry.display.text_layout import paginate, wrap_text


class ScreenManager:
    """Wrap text and send one page of content to the active display driver."""

    def __init__(
        self,
        driver: DisplayDriver,
        width_chars: int,
        height_lines: int,
    ) -> None:
        self.driver = driver
        self.width_chars = width_chars
        self.height_lines = height_lines

    def show(self, screen: Screen) -> None:
        content = f"{screen.title}\n{screen.body}".strip()
        self.show_text(content)

    def show_text(self, text: str) -> None:
        lines = wrap_text(text, self.width_chars)
        page = paginate(lines, self.height_lines)[0]
        self.driver.render(page)
