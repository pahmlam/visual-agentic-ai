from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]
APP_DIR = BASE_DIR / "app"
STATIC_DIR = APP_DIR / "static"
CACHE_DIR = BASE_DIR / "data" / ".cache"
ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH, override=False)

CACHE_DIR.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("MPLCONFIGDIR", str(CACHE_DIR / "matplotlib"))
os.environ.setdefault("YOLO_CONFIG_DIR", str(CACHE_DIR / "ultralytics"))
os.environ.setdefault("XDG_CACHE_HOME", str(CACHE_DIR / "xdg"))
(CACHE_DIR / "matplotlib").mkdir(parents=True, exist_ok=True)
(CACHE_DIR / "ultralytics").mkdir(parents=True, exist_ok=True)
(CACHE_DIR / "xdg").mkdir(parents=True, exist_ok=True)


class Settings:
    def __init__(self) -> None:
        self.app_name = "Visual Agent"
        self.llm_provider = self._provider(os.getenv("LLM_PROVIDER", "ollama"))
        self.vlm_provider = self._provider(os.getenv("VLM_PROVIDER", "ollama"))
        self.text_model = os.getenv("OLLAMA_TEXT_MODEL", "llama3.2:3b")
        self.vision_model = os.getenv("OLLAMA_VISION_MODEL", "llama3.2-vision")
        self.openai_text_model = os.getenv("OPENAI_TEXT_MODEL", "gpt-4.1-nano")
        self.openai_vision_model = os.getenv("OPENAI_VISION_MODEL", "gpt-4o-mini")
        self.gemini_text_model = os.getenv("GEMINI_TEXT_MODEL", "gemini-2.5-flash")
        self.gemini_vision_model = os.getenv("GEMINI_VISION_MODEL", "gemini-2.5-flash")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")
        self.yolo_model_path = Path(
            os.getenv("YOLO_MODEL_PATH", str(BASE_DIR / "yolo11x.pt"))
        )
        self.upload_dir = Path(
            os.getenv("UPLOAD_DIR", str(BASE_DIR / "data" / "uploads"))
        )
        self.max_upload_bytes = int(
            os.getenv("MAX_UPLOAD_BYTES", str(20 * 1024 * 1024))
        )

    @staticmethod
    def _provider(value: str) -> str:
        normalized = value.lower().strip()
        if normalized in {"ollama", "openai", "gemini"}:
            return normalized
        return "ollama"


settings = Settings()
settings.upload_dir.mkdir(parents=True, exist_ok=True)


def reload_settings() -> Settings:
    next_settings = Settings()
    settings.__dict__.update(next_settings.__dict__)
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    return settings


def _parse_env_line(line: str) -> tuple[str | None, str | None]:
    stripped = line.strip()
    if not stripped or stripped.startswith("#") or "=" not in stripped:
        return None, None
    key, value = stripped.split("=", 1)
    return key.strip(), value.strip().strip('"').strip("'")


def read_env_values() -> dict[str, str]:
    if not ENV_PATH.exists():
        return {}
    values: dict[str, str] = {}
    for line in ENV_PATH.read_text().splitlines():
        key, value = _parse_env_line(line)
        if key:
            values[key] = value or ""
    return values


def write_env_values(updates: dict[str, str]) -> None:
    lines = ENV_PATH.read_text().splitlines() if ENV_PATH.exists() else []
    written: set[str] = set()
    next_lines: list[str] = []

    for line in lines:
        key, _ = _parse_env_line(line)
        if key and key in updates:
            value = updates[key]
            next_lines.append(f'{key}="{value}"')
            os.environ[key] = value
            written.add(key)
        else:
            next_lines.append(line)

    for key, value in updates.items():
        if key not in written:
            next_lines.append(f'{key}="{value}"')
            os.environ[key] = value

    ENV_PATH.write_text("\n".join(next_lines).rstrip() + "\n")
