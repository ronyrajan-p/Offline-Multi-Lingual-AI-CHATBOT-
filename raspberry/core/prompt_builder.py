from __future__ import annotations

from .conversation_manager import Message
from .language_detector import SUPPORTED_LANGUAGES


class PromptBuilder:
    def build(self, user_text: str, language: str, history: list[Message]) -> str:
        language_name = SUPPORTED_LANGUAGES.get(language, "English")
        history_lines = [
            f"{message.role}: {message.content}" for message in history[-6:]
        ]
        history_block = "\n".join(history_lines) if history_lines else "No prior messages."

        return (
            "You are a compact offline assistant running on a Raspberry Pi with "
            "a small OLED display. Answer clearly and briefly.\n"
            f"User language: {language_name}.\n"
            "Keep the answer short enough for a small screen.\n\n"
            f"Conversation:\n{history_block}\n\n"
            f"User: {user_text}\n"
            "Assistant:"
        )
