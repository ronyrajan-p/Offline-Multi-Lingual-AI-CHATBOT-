from __future__ import annotations

from raspberry.core.conversation_manager import ConversationManager
from raspberry.core.language_detector import detect_language, normalize_language
from raspberry.core.prompt_builder import PromptBuilder
from raspberry.core.response_formatter import ResponseFormatter
from raspberry.core.utils import normalize_text
from raspberry.services.local_ai import LocalAI
from raspberry.services.offline_translation import OfflineTranslator


class Chatbot:
    def __init__(
        self,
        ai: LocalAI,
        translator: OfflineTranslator,
        formatter: ResponseFormatter,
        prompt_builder: PromptBuilder,
        conversation: ConversationManager,
        language: str = "en",
    ) -> None:
        self.ai = ai
        self.translator = translator
        self.formatter = formatter
        self.prompt_builder = prompt_builder
        self.conversation = conversation
        self.language = normalize_language(language)

    def set_language(self, language: str) -> str:
        self.language = normalize_language(language)
        return self.language

    def respond(self, user_text: str) -> str:
        cleaned = normalize_text(user_text)
        detected_language = detect_language(cleaned, self.language)
        active_language = detected_language or self.language

        model_input = self.translator.translate_to_model_language(
            cleaned,
            active_language,
        )
        prompt = self.prompt_builder.build(
            user_text=model_input,
            language=active_language,
            history=self.conversation.recent_messages(),
        )
        model_response = self.ai.generate(prompt=prompt, user_text=model_input)
        localized_response = self.translator.translate_from_model_language(
            model_response,
            active_language,
        )
        formatted = self.formatter.format(localized_response)

        self.conversation.add_user_message(cleaned)
        self.conversation.add_assistant_message(formatted)
        self.language = active_language
        return formatted
