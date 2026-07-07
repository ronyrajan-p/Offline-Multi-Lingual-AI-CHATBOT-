from __future__ import annotations

"""Local AI service for llama.cpp with explicit fallback behavior."""

import shutil
import subprocess
from pathlib import Path


class LocalAIConfigurationError(RuntimeError):
    """Raised when local AI is required but not configured correctly."""


class LocalAI:
    """Generate responses using llama.cpp or an explicitly enabled fallback.

    The fallback exists so the device controller, display, database, and input
    stack can be tested before the model is installed. For a finished hardware
    model, set `CHATBOT_ALLOW_FALLBACK_AI=false` and provide `CHATBOT_MODEL`.
    """

    def __init__(
        self,
        model_path: Path | None = None,
        llama_binary: str = "llama-cli",
        max_tokens: int = 80,
        timeout_seconds: int = 120,
        allow_fallback: bool = True,
    ) -> None:
        self.model_path = model_path
        self.llama_binary = llama_binary
        self.max_tokens = max_tokens
        self.timeout_seconds = timeout_seconds
        self.allow_fallback = allow_fallback

    def generate(self, prompt: str, user_text: str) -> str:
        """Generate one assistant response."""

        if self.model_path:
            self._validate_llama_config()
            response = self._generate_with_llama(prompt)
            if not response.strip():
                raise LocalAIConfigurationError(
                    "llama.cpp returned an empty response for the current prompt."
                )
            return response
        if not self.allow_fallback:
            raise LocalAIConfigurationError(
                "CHATBOT_MODEL is required when fallback AI is disabled."
            )
        return self._fallback_response(user_text)

    def status(self) -> str:
        """Return a user-readable description of the active AI backend."""

        if self.model_path:
            return "llama.cpp"
        return "fallback"

    def _validate_llama_config(self) -> None:
        if self.model_path is None or not self.model_path.is_file():
            raise LocalAIConfigurationError(
                f"Local model file was not found: {self.model_path}"
            )
        if shutil.which(self.llama_binary) is None:
            raise LocalAIConfigurationError(
                f"llama.cpp binary was not found on PATH: {self.llama_binary}"
            )

    def _generate_with_llama(self, prompt: str) -> str:
        command = [
            self.llama_binary,
            "-m",
            str(self.model_path),
            "-p",
            prompt,
            "-n",
            str(self.max_tokens),
            "--ctx-size",
            "2048",
            "--temp",
            "0.7",
            "--top-p",
            "0.9",
            "--repeat-penalty",
            "1.12",
            "--no-display-prompt",
        ]
        result = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=self.timeout_seconds,
        )
        return self._clean_model_output(result.stdout)

    def _clean_model_output(self, output: str) -> str:
        """Remove ChatML control tokens that may appear in llama.cpp output."""

        cleaned = output.strip()
        if "<|im_end|>" in cleaned:
            cleaned = cleaned.split("<|im_end|>", 1)[0]
        return (
            cleaned.replace("<|im_start|>assistant", "")
            .replace("<|im_start|>", "")
            .replace("<|im_end|>", "")
            .strip()
        )

    def _fallback_response(self, user_text: str) -> str:
        lowered = user_text.lower()
        if "hello" in lowered or "hi" in lowered:
            return "Hello. I am running offline on the Raspberry Pi chatbot."
        if "language" in lowered:
            return "I support English, Tamil, and Hindi with offline translation hooks."
        if "help" in lowered:
            return "Ask a short question. Type /lang en, /lang ta, or /lang hi to switch language."
        return f"Offline fallback response: I received '{user_text}'. Connect a local model in services/local_ai.py for full AI replies."
