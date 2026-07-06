from __future__ import annotations

"""Device controller that connects input, display, chatbot, and storage."""

from raspberry.core.chatbot import Chatbot
from raspberry.core.language_detector import SUPPORTED_LANGUAGES
from raspberry.display.screen_manager import ScreenManager
from raspberry.display.screens import BOOT, PROCESSING, READY, Screen
from raspberry.input.keyboard import KeyboardInput
from raspberry.services.storage import SQLiteStorage


class DeviceController:
    """Main event loop for the physical chatbot device."""

    def __init__(
        self,
        chatbot: Chatbot,
        display: ScreenManager,
        keyboard: KeyboardInput,
        storage: SQLiteStorage,
        default_language: str,
        response_page_seconds: float,
    ) -> None:
        self.chatbot = chatbot
        self.display = display
        self.keyboard = keyboard
        self.storage = storage
        self.session_id: int | None = None
        self.default_language = default_language
        self.response_page_seconds = response_page_seconds

    def startup(self) -> None:
        """Initialize persistent storage and show the ready screen."""

        self.display.show(BOOT)
        self.storage.initialize()
        self.session_id = self.storage.create_session(self.default_language)
        self.storage.save_setting("language", self.default_language)
        self.display.show(READY)

    def run(self) -> None:
        """Read user messages until an exit command is received."""

        self.startup()
        while True:
            message = self.keyboard.read_message()
            if not message:
                continue
            if message.lower() in {"/quit", "/exit"}:
                self.display.show(Screen("Bye", "Offline chatbot stopped"))
                break
            if message.lower().startswith("/lang"):
                self._handle_language_command(message)
                continue
            if message.lower() == "/status":
                self.display.show(Screen("Status", self._status_text()))
                continue

            try:
                self.display.show(PROCESSING)
                response = self.chatbot.respond(message)
                if self.session_id is not None:
                    self.storage.save_message(self.session_id, "user", message)
                    self.storage.save_message(self.session_id, "assistant", response)
                self.display.show_pages(
                    Screen("Response", response),
                    self.response_page_seconds,
                )
            except Exception as exc:
                self.storage.log_error(str(exc))
                self.display.show(Screen("Error", str(exc)))

    def _handle_language_command(self, message: str) -> None:
        """Handle `/lang` commands for manual language selection."""

        parts = message.split(maxsplit=1)
        if len(parts) != 2:
            self.display.show(Screen("Language", "Use /lang en, /lang ta, or /lang hi"))
            return
        language = self.chatbot.set_language(parts[1])
        self.storage.save_setting("language", language)
        label = SUPPORTED_LANGUAGES.get(language, language)
        self.display.show(Screen("Language", f"Selected {label}"))

    def _status_text(self) -> str:
        """Return a concise runtime status suitable for the OLED."""

        ai_status = self.chatbot.ai.status()
        translation_status = self.chatbot.translator.status()
        return f"AI {ai_status}. Translate {translation_status}."
