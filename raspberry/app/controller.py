from __future__ import annotations

"""Device controller that connects input, display, chatbot, and storage."""

import re

from raspberry.core.chatbot import Chatbot
from raspberry.core.language_detector import SUPPORTED_LANGUAGES
from raspberry.display.screen_manager import ScreenManager
from raspberry.display.screens import BOOT, PROCESSING, READY, WAITING_AI, Screen
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
        ai_startup_wait_seconds: float = 60,
    ) -> None:
        self.chatbot = chatbot
        self.display = display
        self.keyboard = keyboard
        self.storage = storage
        self.session_id: int | None = None
        self.default_language = default_language
        self.response_page_seconds = response_page_seconds
        self.ai_startup_wait_seconds = ai_startup_wait_seconds

    def startup(self) -> None:
        """Initialize persistent storage and show the ready screen."""

        print("Python chatbot app started. Commands: /status, /lang en, /lang ta, /lang hi, /exit")
        self.display.show(BOOT)
        self.storage.initialize()
        self.session_id = self.storage.create_session(self.default_language)
        self.storage.save_setting("language", self.default_language)
        self._wait_for_ai_ready()
        self.display.show(READY)

    def _wait_for_ai_ready(self) -> None:
        """Poll llama-server before showing Ready so the first message doesn't stall.

        If `allow_fallback_ai` is enabled, a short wait is enough since the
        fallback responder can take over. If fallback is disabled, this waits
        the full budget because a finished hardware build requires the real
        model.
        """

        if self.chatbot.ai.is_server_ready():
            return
        wait_seconds = (
            self.ai_startup_wait_seconds if not self.chatbot.ai.allow_fallback else 5
        )
        self.display.show(WAITING_AI)
        ready = self.chatbot.ai.wait_until_ready(wait_seconds)
        if not ready and not self.chatbot.ai.allow_fallback:
            self.display.show(
                Screen("AI Offline", "llama-server did not respond in time")
            )

    def run(self) -> None:
        """Read user messages until an exit command is received."""

        self.startup()
        while True:
            try:
                message = self.keyboard.read_message()
            except (EOFError, KeyboardInterrupt):
                self.display.show(Screen("Bye", "Offline chatbot stopped"))
                break
            if not message:
                continue
            if message.lower() in {"/quit", "/exit"}:
                self.display.show(Screen("Bye", "Offline chatbot stopped"))
                break
            language_command = self._parse_language_command(message)
            if language_command is not None:
                self._handle_language_command(language_command)
                continue
            if message.lower() == "/status":
                self.display.show(Screen("Status", self._status_text()))
                continue

            try:
                self.display.show(PROCESSING)
                response = self.chatbot.respond(message)
                if not response.strip():
                    raise RuntimeError("Model returned an empty response.")
                if self.session_id is not None:
                    self.storage.save_message(self.session_id, "user", message)
                    self.storage.save_message(self.session_id, "assistant", response)
                print(f"assistant: {response}")
                self.display.show_pages(
                    Screen("Response", response),
                    self.response_page_seconds,
                )
            except Exception as exc:
                self.storage.log_error(str(exc))
                print(f"error: {exc}")
                self.display.show(Screen("Error", str(exc)))

    def _parse_language_command(self, message: str) -> str | None:
        """Return the requested language from `/lang` command variants."""

        match = re.fullmatch(r"/\s*(?:lang|language)\s+(\S+)", message.strip(), re.I)
        if match is None:
            return None
        return match.group(1)

    def _handle_language_command(self, language_request: str) -> None:
        """Handle `/lang` commands for manual language selection."""

        if not language_request:
            self.display.show(Screen("Language", "Use /lang en, /lang ta, or /lang hi"))
            return
        language = self.chatbot.set_language(language_request)
        self.storage.save_setting("language", language)
        label = SUPPORTED_LANGUAGES.get(language, language)
        print(f"language: {label}")
        self.display.show(Screen("Language", f"Selected {label}"))

    def _status_text(self) -> str:
        """Return a concise runtime status suitable for the OLED."""

        ai_status = self.chatbot.ai.status()
        translation_status = self.chatbot.translator.status()
        label = SUPPORTED_LANGUAGES.get(self.chatbot.language, self.chatbot.language)
        return f"AI {ai_status}. Lang {label}. Translate {translation_status}."
