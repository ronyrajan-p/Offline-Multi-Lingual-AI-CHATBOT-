from __future__ import annotations


SUPPORTED_LANGUAGES = {
    "en": "English",
    "ta": "Tamil",
    "hi": "Hindi",
}


def normalize_language(language: str | None) -> str:
    if not language:
        return "en"
    value = language.strip().lower()
    aliases = {
        "english": "en",
        "eng": "en",
        "tamil": "ta",
        "தமிழ்": "ta",
        "hindi": "hi",
        "हिन्दी": "hi",
        "हिंदी": "hi",
    }
    return aliases.get(value, value if value in SUPPORTED_LANGUAGES else "en")


def detect_language(text: str, fallback: str = "en") -> str:
    """Detect English, Tamil, or Hindi using Unicode ranges.

    This lightweight detector is intentionally offline and dependency-free.
    Manual language selection should still be preferred on the device.
    """

    if any("\u0b80" <= char <= "\u0bff" for char in text):
        return "ta"
    if any("\u0900" <= char <= "\u097f" for char in text):
        return "hi"
    return normalize_language(fallback)
