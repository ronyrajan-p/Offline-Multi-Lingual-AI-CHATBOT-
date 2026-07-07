from __future__ import annotations

"""Display drivers for development and Raspberry Pi OLED hardware."""

from pathlib import Path
from typing import Protocol


class DisplayDriver(Protocol):
    """Small interface used by `ScreenManager`.

    Both console and hardware drivers accept a list of already-wrapped display
    lines. Keeping this contract tiny makes it easier to test without hardware.
    """

    def render(self, lines: list[str]) -> None:
        """Render prepared text lines to the target display."""


class ConsoleOLEDDriver:
    """Console-backed OLED replacement for development and CI checks."""

    def render(self, lines: list[str]) -> None:
        border = "+" + "-" * 24 + "+"
        print(border)
        for line in lines:
            print(f"| {line[:22]:<22} |")
        print(border)


class HardwareOLEDDriver:
    """I2C OLED driver for Raspberry Pi.

    This implementation uses `luma.oled`, which supports common 128x64 SSD1306
    and SH1106 displays. The constructor imports hardware dependencies lazily
    so the project remains runnable on a development machine with the console
    driver.
    """

    def __init__(
        self,
        device_type: str = "ssd1306",
        width: int = 128,
        height: int = 64,
        i2c_port: int = 1,
        i2c_address: int = 0x3C,
        font_path: Path | None = None,
        font_size: int = 10,
        rotate: int = 0,
    ) -> None:
        try:
            from luma.core.interface.serial import i2c
            from luma.oled.device import sh1106, ssd1306
            from PIL import Image, ImageDraw, ImageFont
        except ImportError as exc:
            raise RuntimeError(
                "OLED hardware mode requires: pip install luma.oled pillow"
            ) from exc

        self._image_cls = Image
        self._draw_cls = ImageDraw
        self._font = (
            ImageFont.truetype(str(font_path), font_size)
            if font_path
            else ImageFont.load_default()
        )
        serial = i2c(port=i2c_port, address=i2c_address)
        devices = {
            "ssd1306": ssd1306,
            "sh1106": sh1106,
        }
        if device_type not in devices:
            raise ValueError("OLED device type must be 'ssd1306' or 'sh1106'.")
        self._device = devices[device_type](
            serial,
            width=width,
            height=height,
            rotate=rotate,
        )
        self._line_height = max(font_size + 2, 10)

    def render(self, lines: list[str]) -> None:
        image = self._image_cls.new("L", self._device.size, 0)
        draw = self._draw_cls.Draw(image)
        y = 0
        for line in lines:
            draw.text((0, y), line, font=self._font, fill=255)
            y += self._line_height
        self._device.clear()
        self._device.display(image.convert("1"))
