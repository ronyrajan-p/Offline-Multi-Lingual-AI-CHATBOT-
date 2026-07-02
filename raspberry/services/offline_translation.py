from __future__ import annotations

"""Offline translation service wrapper."""


class TranslationConfigurationError(RuntimeError):
    """Raised when translation is required but unavailable."""


class OfflineTranslator:
    """Translate text offline through Argos Translate when installed.

    When `required` is false, missing Argos packages become a no-op so the
    English-first hardware flow can still be tested. When `required` is true,
    missing translation support fails clearly at runtime.
    """

    def __init__(self, model_language: str = "en", required: bool = False) -> None:
        self.model_language = model_language
        self.required = required
        self._argos = self._load_argos()

    def translate_to_model_language(self, text: str, source_language: str) -> str:
        return self.translate(text, source_language, self.model_language)

    def translate_from_model_language(self, text: str, target_language: str) -> str:
        return self.translate(text, self.model_language, target_language)

    def translate(self, text: str, source_language: str, target_language: str) -> str:
        if source_language == target_language:
            return text
        if self._argos is None:
            if self.required:
                raise TranslationConfigurationError(
                    "Argos Translate is required but not installed."
                )
            return text
        return self._argos.translate(text, source_language, target_language)

    def status(self) -> str:
        """Return a user-readable description of translation availability."""

        if self._argos is None:
            return "passthrough"
        return "Argos"

    def _load_argos(self):
        try:
            import argostranslate.translate as translate
        except ImportError:
            return None
        return translate
