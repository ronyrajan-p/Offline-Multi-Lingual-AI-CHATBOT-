from raspberry.core.conversation_manager import ConversationManager
from raspberry.core.language_detector import detect_language, normalize_language
from raspberry.core.prompt_builder import PromptBuilder
from raspberry.core.response_formatter import ResponseFormatter
from raspberry.display.text_layout import paginate, wrap_text
from raspberry.app.main import build_controller
from raspberry.services.local_ai import LocalAI


def test_language_detection_unicode_ranges():
    assert detect_language("hello") == "en"
    assert detect_language("\u0bb5\u0ba3\u0b95\u0bcd\u0b95\u0bae\u0bcd") == "ta"
    assert detect_language("\u0928\u092e\u0938\u094d\u0924\u0947") == "hi"


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


def test_text_layout_paginates_response_for_oled():
    wrapped = wrap_text("one two three four", 7)
    assert paginate(wrapped, 2) == [["one two", "three"], ["four"]]


def test_prompt_builder_uses_qwen_chatml_for_tamil():
    prompt = PromptBuilder().build("weather?", "ta", [])
    assert "<|im_start|>system" in prompt
    assert "Reply only in natural Tamil script" in prompt
    assert "<|im_start|>assistant" in prompt


def test_prompt_builder_uses_qwen_chatml_for_hindi():
    prompt = PromptBuilder().build("weather?", "hi", [])
    assert "<|im_start|>system" in prompt
    assert "Reply only in natural Hindi using Devanagari script" in prompt
    assert "Do not give a prewritten Hindi greeting" in prompt
    assert "<|im_start|>assistant" in prompt


def test_controller_accepts_language_command_variants():
    controller = build_controller()
    assert controller._parse_language_command("/lang hi") == "hi"
    assert controller._parse_language_command("/ lang hi") == "hi"
    assert controller._parse_language_command("/language ta") == "ta"
    assert controller._parse_language_command("What is your name") is None


def test_llama_command_is_non_interactive():
    ai = LocalAI(model_path=__file__)
    command = ai._build_llama_command("prompt", "--no-conversation")
    assert "--no-conversation" in command
    assert "--log-disable" in command


def test_llama_output_cleaner_removes_echoed_prompt():
    ai = LocalAI(model_path=__file__)
    output = "<|im_start|>system\nx\n<|im_start|>assistant\nhello<|im_end|>"
    assert ai._clean_model_output(output) == "hello"
