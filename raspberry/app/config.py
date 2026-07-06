"""Application configuration for the Raspberry Pi chatbot.

Every hardware-dependent value is controlled here or by an environment
variable. This keeps the program honest: development can use the console
simulator, while the physical model can opt into the real OLED and local model
paths without editing business logic.
"""

from dataclasses import dataclass
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


def _env_bool(name: str, default: bool) -> bool:
    """Read a boolean environment variable using clear true/false values."""

    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int) -> int:
    """Read an integer environment variable and fail fast when invalid."""

    value = os.getenv(name)
    if value is None:
        return default
    return int(value, 0)


@dataclass(frozen=True)
class AppConfig:
    """Runtime settings for the offline device.

    `display_driver` accepts `console` for development or `ssd1306_i2c` for a
    real I2C OLED. `allow_fallback_ai` keeps the program runnable before a GGUF
    model is installed; set it to `false` on the finished hardware build so
    missing AI configuration is surfaced immediately.
    """

    database_path: Path = BASE_DIR / "database" / "chatbot.sqlite"
    schema_path: Path = BASE_DIR / "database" / "schema.sql"
    model_path: Path | None = None
    translations_path: Path = BASE_DIR / "translations" / "argos-packages"
    display_width_chars: int = 21
    display_height_lines: int = 6
    display_width_pixels: int = 128
    display_height_pixels: int = 64
    display_i2c_port: int = 1
    display_i2c_address: int = 0x3C
    display_page_seconds: float = 2.5
    max_response_chars: int = 420
    llama_binary: str = "llama-cli"
    llama_timeout_seconds: int = 120
    local_ai_max_tokens: int = 80
    default_language: str = "en"
    display_driver: str = "console"
    allow_fallback_ai: bool = True
    require_translation: bool = False


config = AppConfig(
    database_path=Path(os.getenv("CHATBOT_DB", str(BASE_DIR / "database" / "chatbot.sqlite"))),
    schema_path=Path(os.getenv("CHATBOT_SCHEMA", str(BASE_DIR / "database" / "schema.sql"))),
    model_path=Path(os.getenv("CHATBOT_MODEL")) if os.getenv("CHATBOT_MODEL") else None,
    translations_path=Path(os.getenv("CHATBOT_TRANSLATIONS", str(BASE_DIR / "translations" / "argos-packages"))),
    display_width_chars=_env_int("CHATBOT_DISPLAY_CHARS", 21),
    display_height_lines=_env_int("CHATBOT_DISPLAY_LINES", 6),
    display_width_pixels=_env_int("CHATBOT_OLED_WIDTH", 128),
    display_height_pixels=_env_int("CHATBOT_OLED_HEIGHT", 64),
    display_i2c_port=_env_int("CHATBOT_I2C_PORT", 1),
    display_i2c_address=_env_int("CHATBOT_I2C_ADDRESS", 0x3C),
    display_page_seconds=float(os.getenv("CHATBOT_DISPLAY_PAGE_SECONDS", "2.5")),
    max_response_chars=_env_int("CHATBOT_MAX_RESPONSE_CHARS", 420),
    llama_binary=os.getenv("CHATBOT_LLAMA_BINARY", "llama-cli"),
    llama_timeout_seconds=_env_int("CHATBOT_LLAMA_TIMEOUT", 120),
    local_ai_max_tokens=_env_int("CHATBOT_AI_MAX_TOKENS", 80),
    default_language=os.getenv("CHATBOT_LANGUAGE", "en"),
    display_driver=os.getenv("CHATBOT_DISPLAY_DRIVER", "console"),
    allow_fallback_ai=_env_bool("CHATBOT_ALLOW_FALLBACK_AI", True),
    require_translation=_env_bool("CHATBOT_REQUIRE_TRANSLATION", False),
)
