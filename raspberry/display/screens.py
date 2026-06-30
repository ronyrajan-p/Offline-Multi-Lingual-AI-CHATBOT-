from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Screen:
    title: str
    body: str = ""


BOOT = Screen("Boot", "Loading offline chatbot")
READY = Screen("Ready", "Type a message")
PROCESSING = Screen("Thinking", "Generating response")
