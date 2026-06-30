from __future__ import annotations


class ConsoleOLEDDriver:
    """Console-backed OLED replacement for development."""

    def render(self, lines: list[str]) -> None:
        border = "+" + "-" * 24 + "+"
        print(border)
        for line in lines:
            print(f"| {line[:22]:<22} |")
        print(border)


class HardwareOLEDDriver:
    """Placeholder for SSD1306/luma.oled integration on Raspberry Pi."""

    def __init__(self) -> None:
        raise NotImplementedError(
            "Install an OLED library and implement hardware rendering here."
        )
