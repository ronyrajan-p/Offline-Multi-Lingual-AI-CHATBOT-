from raspberry.core.conversation_manager import ConversationManager
from raspberry.core.language_detector import detect_language, normalize_language
from raspberry.core.response_formatter import ResponseFormatter


def test_language_detection_unicode_ranges():
    assert detect_language("hello") == "en"
    assert detect_language("வணக்கம்") == "ta"
    assert detect_language("नमस्ते") == "hi"


def test_language_aliases():
    assert normalize_language("Tamil") == "ta"
    assert normalize_language("Hindi") == "hi"
    assert normalize_language("English") == "en"


def test_conversation_keeps_recent_messages():
    conversation = ConversationManager(max_messages=2)
    conversation.add_user_message("one")
    conversation.add_assistant_message("two")
    conversation.add_user_message("three")
    assert [message.content for message in conversation.recent_messages()] == [
        "two",
        "three",
    ]


def test_response_formatter_truncates():
    formatter = ResponseFormatter(max_chars=8)
    assert formatter.format("hello world") == "hello..."
