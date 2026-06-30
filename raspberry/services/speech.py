from __future__ import annotations


class SpeechService:
    def speak(self, text: str) -> None:
        raise NotImplementedError("Offline text-to-speech can be added with eSpeak NG.")
