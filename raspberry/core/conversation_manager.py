from __future__ import annotations

from dataclasses import dataclass, field

from .utils import utc_now_iso


@dataclass(frozen=True)
class Message:
    role: str
    content: str
    created_at: str = field(default_factory=utc_now_iso)


class ConversationManager:
    def __init__(self, max_messages: int = 8) -> None:
        self.max_messages = max_messages
        self.messages: list[Message] = []

    def add_user_message(self, content: str) -> None:
        self._add("user", content)

    def add_assistant_message(self, content: str) -> None:
        self._add("assistant", content)

    def recent_messages(self) -> list[Message]:
        return list(self.messages[-self.max_messages :])

    def clear(self) -> None:
        self.messages.clear()

    def _add(self, role: str, content: str) -> None:
        self.messages.append(Message(role=role, content=content))
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages :]
