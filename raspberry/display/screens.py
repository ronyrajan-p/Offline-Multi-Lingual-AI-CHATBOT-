from __future__ import annotations

"""Named screens shown by the device controller."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Screen:
    """Simple OLED screen made from a title and body text."""

    title: str
    body: str = ""


BOOT = Screen("Boot", "Loading offline chatbot")
READY = Screen("Ready", "Type a message")
PROCESSING = Screen("Thinking", "Generating response")
