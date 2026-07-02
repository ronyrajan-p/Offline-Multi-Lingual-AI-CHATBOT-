from __future__ import annotations

"""Runtime composition for the Raspberry Pi chatbot application."""

from raspberry.app.config import config
from raspberry.app.controller import DeviceController
from raspberry.core.chatbot import Chatbot
from raspberry.core.conversation_manager import ConversationManager
from raspberry.core.prompt_builder import PromptBuilder
from raspberry.core.response_formatter import ResponseFormatter
from raspberry.display.oled_driver import ConsoleOLEDDriver, HardwareOLEDDriver
from raspberry.display.screen_manager import ScreenManager
from raspberry.input.keyboard import KeyboardInput
from raspberry.services.local_ai import LocalAI
from raspberry.services.offline_translation import OfflineTranslator
from raspberry.services.storage import SQLiteStorage


def build_controller() -> DeviceController:
    """Create the controller with services selected from configuration."""

    storage = SQLiteStorage(config.database_path, config.schema_path)
    ai = LocalAI(
        model_path=config.model_path,
        llama_binary=config.llama_binary,
        max_tokens=config.local_ai_max_tokens,
        timeout_seconds=config.llama_timeout_seconds,
        allow_fallback=config.allow_fallback_ai,
    )
    translator = OfflineTranslator(required=config.require_translation)
    chatbot = Chatbot(
        ai=ai,
        translator=translator,
        formatter=ResponseFormatter(config.max_response_chars),
        prompt_builder=PromptBuilder(),
        conversation=ConversationManager(),
        language=config.default_language,
    )
    driver = _build_display_driver()
    display = ScreenManager(
        driver=driver,
        width_chars=config.display_width_chars,
        height_lines=config.display_height_lines,
    )
    return DeviceController(
        chatbot=chatbot,
        display=display,
        keyboard=KeyboardInput(),
        storage=storage,
        default_language=config.default_language,
    )


def _build_display_driver():
    """Select the configured display driver."""

    if config.display_driver == "console":
        return ConsoleOLEDDriver()
    if config.display_driver == "ssd1306_i2c":
        return HardwareOLEDDriver(
            width=config.display_width_pixels,
            height=config.display_height_pixels,
            i2c_port=config.display_i2c_port,
            i2c_address=config.display_i2c_address,
        )
    raise ValueError(
        "CHATBOT_DISPLAY_DRIVER must be either 'console' or 'ssd1306_i2c'."
    )


def main() -> None:
    """Run the offline chatbot until the user exits."""

    build_controller().run()


if __name__ == "__main__":
    main()
