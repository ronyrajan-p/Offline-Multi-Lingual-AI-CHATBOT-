"""Dependency-free verification checks for the offline chatbot.

Run from the project root with:

    python -m raspberry.tests.run_checks
"""

from raspberry.core.conversation_manager import ConversationManager
from raspberry.core.language_detector import detect_language, normalize_language
from raspberry.core.prompt_builder import PromptBuilder
from raspberry.core.response_formatter import ResponseFormatter
from raspberry.display.text_layout import paginate, wrap_text
from raspberry.services.local_ai import LocalAI, LocalAIConfigurationError


def main() -> None:
    """Run core assertions without requiring pytest."""

    assert detect_language("hello") == "en"
    assert detect_language("\u0bb5\u0ba3\u0b95\u0bcd\u0b95\u0bae\u0bcd") == "ta"
    assert detect_language("\u0928\u092e\u0938\u094d\u0924\u0947") == "hi"
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
    wrapped = wrap_text("one two three four", 7)
    assert paginate(wrapped, 2) == [["one two", "three"], ["four"]]

    tamil_prompt = PromptBuilder().build("weather?", "ta", [])
    assert "<|im_start|>system" in tamil_prompt
    assert "Reply only in natural Tamil script" in tamil_prompt
    assert "<|im_start|>assistant" in tamil_prompt
    hindi_prompt = PromptBuilder().build("weather?", "hi", [])
    assert "<|im_start|>system" in hindi_prompt
    assert "Reply only in natural Hindi using Devanagari script" in hindi_prompt
    assert "Do not give a prewritten Hindi greeting" in hindi_prompt
    assert "<|im_start|>assistant" in hindi_prompt

    raised = False
    try:
        LocalAI(allow_fallback=False).generate("prompt", "hello")
    except LocalAIConfigurationError:
        raised = True
    assert raised

    print("checks passed")


if __name__ == "__main__":
    main()
