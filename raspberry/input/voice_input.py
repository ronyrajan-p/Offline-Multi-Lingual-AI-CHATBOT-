from __future__ import annotations

"""Offline voice input adapter.

Voice input is optional and must be configured with an offline speech-to-text
engine before it is connected to the controller.
"""


class VoiceInput:
    """Read messages from a local speech-to-text engine when configured."""

    def read_message(self) -> str:
        """Read one spoken message."""

        raise RuntimeError("Voice input is not configured for this device build.")
