from __future__ import annotations
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, model_validator

class Settings(BaseSettings):
    # pydantic v2 config
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        extra="ignore",
        arbitrary_types_allowed=True,
    )

    # --- Required/optional secrets ---
    GEMINI_API_KEY: str
    GEMINI_MODEL: str | None = 'gemini-1.5-flash'
    
    TELEGRAM_BOT_TOKEN: str | None = None
    TELEGRAM_CHAT_ID: str | None = None

    # --- General ---
    TZ: str = "Europe/Istanbul"

    # --- Project dirs (can be overridden via env) ---
    BASE_DIR: Path = Path("/home/reekroo/ai_hub")
    RUNTIME_DIR: Path | None = None
    LOG_DIR: Path | None = None
    STATE_DIR: Path | None = None

    # --- Inputs (monitors) ---
    WEATHER_JSON: Path = Path("/run/monitors/weather/latest.json")
    QUAKES_JSON: Path = Path("/run/monitors/earthquakes/last7d.json")
    MOVIES_ROOT: Path = Path("/media/nvme/movies")

    @model_validator(mode="after")
    def _fill_dirs(self) -> "Settings":
        # Подставляем значения по умолчанию на основе BASE_DIR, если явно не заданы
        if self.RUNTIME_DIR is None:
            self.RUNTIME_DIR = self.BASE_DIR / "run"
        if self.LOG_DIR is None:
            self.LOG_DIR = self.BASE_DIR / "logs"
        if self.STATE_DIR is None:
            self.STATE_DIR = self.BASE_DIR / "state"
        return self
