from __future__ import annotations

"""Console keyboard input adapter used during development and USB testing."""


class KeyboardInput:
    """Read messages from standard input."""

    def read_message(self) -> str:
        """Prompt for and return one user message."""

        return input("chatbot> ").strip()
