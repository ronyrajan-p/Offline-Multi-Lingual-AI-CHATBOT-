from __future__ import annotations

from raspberry.app.config import config
from raspberry.app.controller import DeviceController
from raspberry.core.chatbot import Chatbot
from raspberry.core.conversation_manager import ConversationManager
from raspberry.core.prompt_builder import PromptBuilder
from raspberry.core.response_formatter import ResponseFormatter
from raspberry.display.oled_driver import ConsoleOLEDDriver
from raspberry.display.screen_manager import ScreenManager
from raspberry.input.keyboard import KeyboardInput
from raspberry.services.local_ai import LocalAI
from raspberry.services.offline_translation import OfflineTranslator
from raspberry.services.storage import SQLiteStorage


def build_controller() -> DeviceController:
    storage = SQLiteStorage(config.database_path, config.schema_path)
    chatbot = Chatbot(
        ai=LocalAI(model_path=config.model_path),
        translator=OfflineTranslator(),
        formatter=ResponseFormatter(config.max_response_chars),
        prompt_builder=PromptBuilder(),
        conversation=ConversationManager(),
        language=config.default_language,
    )
    display = ScreenManager(
        driver=ConsoleOLEDDriver(),
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


def main() -> None:
    build_controller().run()


if __name__ == "__main__":
    main()
