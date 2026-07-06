from __future__ import annotations

"""Prompt construction for compact local model responses.

Qwen2.5 Instruct follows a ChatML-style format. Using that format gives the
model a clearer separation between system rules, conversation history, and the
current user message than a plain "User: ... Assistant:" completion prompt.
"""

from .conversation_manager import Message
from .language_detector import SUPPORTED_LANGUAGES


class PromptBuilder:
    """Build prompts that favor short OLED-friendly answers."""

    def build(self, user_text: str, language: str, history: list[Message]) -> str:
        """Create a local-model prompt from user text and recent history."""

        language_name = SUPPORTED_LANGUAGES.get(language, "English")
        language_rule = self._language_rule(language, language_name)
        history_block = self._format_history(history[-6:])

        return (
            "<|im_start|>system\n"
            "You are a compact offline assistant running on a Raspberry Pi with "
            "a small OLED display.\n"
            "Answer the user's exact message with a fresh response. Do not use "
            "fixed templates, memorized demo replies, or unrelated examples.\n"
            "Keep the answer short enough for a small screen.\n"
            f"{language_rule}\n"
            "<|im_end|>\n"
            f"{history_block}"
            "<|im_start|>user\n"
            f"{user_text}\n"
            "<|im_end|>\n"
            "<|im_start|>assistant\n"
        )

    def _language_rule(self, language: str, language_name: str) -> str:
        """Return a strict response-language instruction for the model."""

        if language == "ta":
            return (
                "Reply only in natural Tamil script. Do not answer in English. "
                "Do not give a prewritten Tamil greeting unless the user asks "
                "for a greeting."
            )
        if language == "hi":
            return (
                "Reply only in natural Hindi using Devanagari script. Do not "
                "answer in English unless the user explicitly asks for English. "
                "Do not give a prewritten Hindi greeting unless the user asks "
                "for a greeting."
            )
        return f"Reply in {language_name}."

    def _format_history(self, history: list[Message]) -> str:
        """Format recent messages as ChatML turns."""

        if not history:
            return ""

        turns: list[str] = []
        for message in history:
            role = "assistant" if message.role == "assistant" else "user"
            turns.append(
                f"<|im_start|>{role}\n"
                f"{message.content}\n"
                "<|im_end|>\n"
            )
        return "".join(turns)
