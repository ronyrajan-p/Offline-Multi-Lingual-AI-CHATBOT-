from __future__ import annotations

"""In-memory conversation history for compact local prompts."""

from dataclasses import dataclass, field

from .utils import utc_now_iso


@dataclass(frozen=True)
class Message:
    """One chat message stored in the rolling conversation window."""

    role: str
    content: str
    created_at: str = field(default_factory=utc_now_iso)


class ConversationManager:
    """Keep only recent messages so Raspberry Pi prompts stay small."""

    def __init__(self, max_messages: int = 8) -> None:
        self.max_messages = max_messages
        self.messages: list[Message] = []

    def add_user_message(self, content: str) -> None:
        """Store a user message."""

        self._add("user", content)

    def add_assistant_message(self, content: str) -> None:
        """Store an assistant message."""

        self._add("assistant", content)

    def recent_messages(self) -> list[Message]:
        """Return the bounded recent message list."""

        return list(self.messages[-self.max_messages :])

    def clear(self) -> None:
        """Remove all in-memory messages."""

        self.messages.clear()

    def _add(self, role: str, content: str) -> None:
        """Append a message and enforce the rolling history limit."""

        self.messages.append(Message(role=role, content=content))
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages :]
