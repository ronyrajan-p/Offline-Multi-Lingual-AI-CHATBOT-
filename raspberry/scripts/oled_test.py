from __future__ import annotations

"""OLED-only diagnostic screen test.

Run from the project root on the Raspberry Pi:

    python3 -m raspberry.scripts.oled_test
"""

from raspberry.app.config import config
from raspberry.app.main import _build_display_driver
from raspberry.display.screen_manager import ScreenManager
from raspberry.display.screens import Screen


def main() -> None:
    """Render known-good OLED screens without loading the LLM."""

    display = ScreenManager(
        driver=_build_display_driver(),
        width_chars=config.display_width_chars,
        height_lines=config.display_height_lines,
    )
    display.show(Screen("OLED Test", "English OK"))
    input("Press Enter for response page test...")
    display.show_pages(
        Screen(
            "Response",
            "This is a chatbot response test. If this text is readable, OLED "
            "response rendering is connected correctly.",
        ),
        config.display_page_seconds,
    )
    input("Press Enter to clear...")
    display.show(Screen("Done", "OLED test complete"))


if __name__ == "__main__":
    main()
