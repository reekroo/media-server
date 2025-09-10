from __future__ import annotations
from pathlib import Path
import tomllib
import os
import zoneinfo
from typing import Dict, Any, List

from pydantic import Field, model_validator, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from config_models.daily_config import DailyConfig
from config_models.dinner_config import DinnerConfig
from config_models.media_config import MediaConfig
from config_models.sys_config import SysConfig
from config_models.logs_config import LogsConfig
from config_models.feed_based_config import FeedBasedConfig
from config_models.schedule_config import ScheduleConfig

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent 

class Settings(BaseSettings):
    MODEL_CONFIG = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        extra="ignore",
        arbitrary_types_allowed=True,
    )

    MODEL_LANGUAGE: str = Field(
        default="ru", 
        description="Default communication language")
    
    MODEL_TIMEZONE: str = Field(
        default_factory=lambda: os.environ.get("TZ", "Europe/Istanbul"),
        description="IANA timezone for scheduler (e.g. Europe/Istanbul, UTC)",
    )

    GEMINI_API_KEY: str
    GEMINI_MODEL: str = 'gemini-2.5-flash'
    TELEGRAM_BOT_TOKEN: str | None = None
    TELEGRAM_CHAT_ID: str | None = None
    TELEGRAM_ADMIN_IDS: List[str] = Field(default_factory=list)

    BASE_DIR: Path = PROJECT_ROOT
    STATE_DIR: Path = PROJECT_ROOT / "state"

    schedule: ScheduleConfig | None = None
    chat: Dict[str, Any] | None = None
    daily: DailyConfig | None = None
    dinner: DinnerConfig | None = None
    media: MediaConfig | None = None
    entertainment: FeedBasedConfig | None = None
    news: FeedBasedConfig | None = None
    news_tr: FeedBasedConfig | None = None
    news_by: FeedBasedConfig | None = None
    gaming: FeedBasedConfig | None = None
    sys: SysConfig | None = None
    logs: LogsConfig | None = None

    @field_validator("TZ")
    @classmethod
    def _validate_tz(cls, v: str) -> str:
        try:
            zoneinfo.ZoneInfo(v)
        except Exception:
            return "UTC"
        return v

    @field_validator("TELEGRAM_ADMIN_IDS", mode='before')
    @classmethod
    def _parse_admin_ids(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            return [item.strip() for item in v.split(',') if item.strip()]
        
        if isinstance(v, (int, float)):
            return [str(v)]
            
        if v is None:
            return []
        
        return v

    @model_validator(mode='after')
    def _load_and_parse_toml_configs(self) -> 'Settings':
        config_dir = self.BASE_DIR / "configs"

        daily_path = config_dir / "daily.toml"
        if daily_path.exists():
            data = tomllib.loads(daily_path.read_text("utf-8"))
            self.daily = DailyConfig(**data.get("brief", {}))

        media_path = config_dir / "media.toml"
        if media_path.exists():
            data = tomllib.loads(media_path.read_text("utf-8"))
            relative_state_path = Path(data.get('state_path', 'media_index.json')).name
            data['state_path'] = self.STATE_DIR / relative_state_path
            self.media = MediaConfig(**data)
            
        sys_path = config_dir / "sys.toml"
        if sys_path.exists():
            self.sys = SysConfig(**tomllib.loads(sys_path.read_text("utf-8")))

        news_path = config_dir / "news.toml"
        if news_path.exists():
            self.news = FeedBasedConfig(**tomllib.loads(news_path.read_text("utf-8")))
            
        gaming_path = config_dir / "gaming.toml"
        if gaming_path.exists():
            self.gaming = FeedBasedConfig(**tomllib.loads(gaming_path.read_text("utf--8")))
        
        chat_path = config_dir / "chat.toml"
        if chat_path.exists():
            self.chat = tomllib.loads(chat_path.read_text("utf-8"))

        schedule_path = config_dir / "schedule.toml"
        if schedule_path.exists():
            self.schedule = ScheduleConfig(**tomllib.loads(schedule_path.read_text("utf-8")))

        return self