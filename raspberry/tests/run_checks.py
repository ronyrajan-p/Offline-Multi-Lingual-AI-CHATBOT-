"""Dependency-free verification checks for the offline chatbot.

Run from the project root with:

    python -m raspberry.tests.run_checks
"""

from raspberry.core.conversation_manager import ConversationManager
from raspberry.core.language_detector import detect_language, normalize_language
from raspberry.core.response_formatter import ResponseFormatter
from raspberry.services.local_ai import LocalAI, LocalAIConfigurationError


def main() -> None:
    """Run core assertions without requiring pytest."""

    assert detect_language("hello") == "en"
    assert detect_language("வணக்கம்") == "ta"
    assert detect_language("नमस्ते") == "hi"
    assert normalize_language("Tamil") == "ta"

    conversation = ConversationManager(max_messages=2)
    conversation.add_user_message("one")
    conversation.add_assistant_message("two")
    conversation.add_user_message("three")
    assert [message.content for message in conversation.recent_messages()] == [
        "two",
        "three",
    ]

    assert ResponseFormatter(max_chars=8).format("hello world") == "hello..."

    raised = False
    try:
        LocalAI(allow_fallback=False).generate("prompt", "hello")
    except LocalAIConfigurationError:
        raised = True
    assert raised

    print("checks passed")


if __name__ == "__main__":
    main()
