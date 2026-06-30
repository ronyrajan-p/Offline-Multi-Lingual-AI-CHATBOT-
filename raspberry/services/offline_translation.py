from __future__ import annotations


class OfflineTranslator:
    """Offline translation facade.

    If Argos Translate is installed later, wire it in here. The current fallback
    keeps the program fully runnable without internet or extra packages.
    """

    def __init__(self, model_language: str = "en") -> None:
        self.model_language = model_language
        self._argos = self._load_argos()

    def translate_to_model_language(self, text: str, source_language: str) -> str:
        return self.translate(text, source_language, self.model_language)

    def translate_from_model_language(self, text: str, target_language: str) -> str:
        return self.translate(text, self.model_language, target_language)

    def translate(self, text: str, source_language: str, target_language: str) -> str:
        if source_language == target_language:
            return text
        if self._argos is None:
            return text
        return self._argos.translate(text, source_language, target_language)

    def _load_argos(self):
        try:
            import argostranslate.translate as translate
        except ImportError:
            return None
        return translate
