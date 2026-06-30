from __future__ import annotations

import subprocess
from pathlib import Path


class LocalAI:
    """Local AI facade for llama.cpp with a deterministic fallback."""

    def __init__(
        self,
        model_path: Path | None = None,
        llama_binary: str | None = None,
        max_tokens: int = 80,
    ) -> None:
        self.model_path = model_path
        self.llama_binary = llama_binary
        self.max_tokens = max_tokens

    def generate(self, prompt: str, user_text: str) -> str:
        if self.llama_binary and self.model_path:
            return self._generate_with_llama(prompt)
        return self._fallback_response(user_text)

    def _generate_with_llama(self, prompt: str) -> str:
        command = [
            self.llama_binary or "llama-cli",
            "-m",
            str(self.model_path),
            "-p",
            prompt,
            "-n",
            str(self.max_tokens),
        ]
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=120,
        )
        return result.stdout.strip()

    def _fallback_response(self, user_text: str) -> str:
        lowered = user_text.lower()
        if "hello" in lowered or "hi" in lowered:
            return "Hello. I am running offline on the Raspberry Pi chatbot."
        if "language" in lowered:
            return "I support English, Tamil, and Hindi with offline translation hooks."
        if "help" in lowered:
            return "Ask a short question. Type /lang en, /lang ta, or /lang hi to switch language."
        return f"Offline fallback response: I received '{user_text}'. Connect a local model in services/local_ai.py for full AI replies."
