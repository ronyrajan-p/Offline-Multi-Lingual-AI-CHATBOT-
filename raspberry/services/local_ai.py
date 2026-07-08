from __future__ import annotations

"""Local AI service client for a persistent llama-server process.

Earlier versions of this service shelled out to `llama-cli` fresh for every
message. That approach broke on current llama.cpp builds: `llama-cli`
defaults into an interactive chat TUI once it detects a chat-capable model,
and that TUI writes its banner straight to the controlling terminal,
bypassing captured stdout entirely. It also reloaded the full GGUF model
from disk on every single turn, which is far too slow for a Pi 5.

This client instead talks to `llama-server` (llama.cpp's built-in HTTP
server) over `/health` and `/completion`. The server loads the model exactly
once at boot, and every chat turn is a short-lived HTTP request against
already-resident weights.
"""

import json
import time
import urllib.error
import urllib.request


class LocalAIConfigurationError(RuntimeError):
    """Raised when local AI is required but not configured correctly."""


class LocalAI:
    """Generate responses through a running llama-server instance.

    A `llama-server` process, started separately as its own systemd service,
    must already be listening at `host:port` with the target model loaded.
    The fallback exists so the device controller, display, database, and
    input stack can be tested before `llama-server` is running. For a
    finished hardware build, set `CHATBOT_ALLOW_FALLBACK_AI=false` so a dead
    or unreachable server fails loudly instead of silently degrading.
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8080,
        max_tokens: int = 80,
        request_timeout_seconds: int = 60,
        allow_fallback: bool = True,
    ) -> None:
        self.base_url = f"http://{host}:{port}"
        self.max_tokens = max_tokens
        self.request_timeout_seconds = request_timeout_seconds
        self.allow_fallback = allow_fallback

    def generate(self, prompt: str, user_text: str) -> str:
        """Generate one assistant response."""

        if self.is_server_ready():
            response = self._generate_via_server(prompt)
            if not response.strip():
                raise LocalAIConfigurationError(
                    "llama-server returned an empty response for the current prompt."
                )
            return response
        if not self.allow_fallback:
            raise LocalAIConfigurationError(
                f"llama-server is not reachable at {self.base_url}. "
                "Start the llama-server.service unit before the chatbot."
            )
        return self._fallback_response(user_text)

    def status(self) -> str:
        """Return a user-readable description of the active AI backend."""

        if self.is_server_ready():
            return "llama-server"
        return "fallback"

    def is_server_ready(self, timeout_seconds: float = 2.0) -> bool:
        """Return whether llama-server has finished loading the model."""

        try:
            with urllib.request.urlopen(
                f"{self.base_url}/health", timeout=timeout_seconds
            ) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except (urllib.error.URLError, ValueError, OSError):
            return False
        return payload.get("status") == "ok"

    def wait_until_ready(self, timeout_seconds: float, poll_seconds: float = 1.0) -> bool:
        """Poll `/health` until llama-server is ready, up to a deadline.

        Used at controller startup so the OLED can show a clear waiting
        screen while the server finishes loading the model, instead of the
        first chat message failing.
        """

        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            if self.is_server_ready():
                return True
            time.sleep(poll_seconds)
        return self.is_server_ready()

    def _generate_via_server(self, prompt: str) -> str:
        payload = {
            "prompt": prompt,
            "n_predict": self.max_tokens,
            "temperature": 0.7,
            "top_p": 0.9,
            "repeat_penalty": 1.12,
            "stop": ["<|im_end|>", "<|im_start|>"],
            "cache_prompt": True,
        }
        request = urllib.request.Request(
            f"{self.base_url}/completion",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(
                request, timeout=self.request_timeout_seconds
            ) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise LocalAIConfigurationError(
                f"llama-server request failed: {exc}"
            ) from exc
        except TimeoutError as exc:
            raise LocalAIConfigurationError(
                f"llama-server did not respond within {self.request_timeout_seconds}s."
            ) from exc
        content = body.get("content", "")
        return self._clean_model_output(content)

    def _clean_model_output(self, output: str) -> str:
        """Remove ChatML control tokens that may appear in the completion."""

        cleaned = output.strip()
        if "<|im_start|>assistant" in cleaned:
            cleaned = cleaned.rsplit("<|im_start|>assistant", 1)[-1]
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
        return f"Offline fallback response: I received '{user_text}'. Start llama-server and set CHATBOT_ALLOW_FALLBACK_AI=false for full AI replies."
