from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class AppConfig:
    """Runtime settings for the offline device."""

    database_path: Path = BASE_DIR / "database" / "chatbot.sqlite"
    schema_path: Path = BASE_DIR / "database" / "schema.sql"
    model_path: Path = BASE_DIR / "models" / "local-llm-files"
    translations_path: Path = BASE_DIR / "translations" / "argos-packages"
    display_width_chars: int = 21
    display_height_lines: int = 6
    max_response_chars: int = 420
    default_language: str = "en"
    use_console_display: bool = True


config = AppConfig()
