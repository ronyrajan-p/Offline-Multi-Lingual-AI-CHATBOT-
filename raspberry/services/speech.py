from __future__ import annotations

"""Offline speech output adapter."""


class SpeechService:
    """Speak text through an offline text-to-speech engine when configured."""

    def speak(self, text: str) -> None:
        """Speak text through the configured TTS backend."""

        raise RuntimeError("Speech output is not configured for this device build.")
