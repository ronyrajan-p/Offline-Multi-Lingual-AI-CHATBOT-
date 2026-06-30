from __future__ import annotations


class VoiceInput:
    def read_message(self) -> str:
        raise NotImplementedError("Offline speech-to-text can be added with Vosk.")
