from __future__ import annotations
from pathlib import Path
import tomllib
from typing import Dict, Any, List

from pydantic import BaseModel, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent 

class DailyConfig(BaseModel):
    include_quakes: bool = True

class MediaRecommenderConfig(BaseModel):
    language: str = "en"
    genres: List[str] = Field(default_factory=list)

class MediaConfig(BaseModel):
    enabled: bool = True
    root: Path = Path("/media")
    max_depth: int = 6
    include_ext: List[str] = Field(default_factory=lambda: [".mkv", ".mp4"])
    state_path: Path
    recommender: MediaRecommenderConfig = Field(default_factory=MediaRecommenderConfig)
    
class SysPatternsConfig(BaseModel):
    disk: List[str] = Field(default_factory=list)
    net: List[str] = Field(default_factory=list)
    app: List[str] = Field(default_factory=list)

class SysConfig(BaseModel):
    enabled: bool = True
    lookback: str = "24h"
    min_priority: str = "warning"
    max_restarts: int = 3
    units: List[str] = Field(default_factory=list)
    patterns: SysPatternsConfig = Field(default_factory=SysPatternsConfig)

class FeedBasedConfig(BaseModel):
    enabled: bool = False
    max_items: int = 20
    feeds: Dict[str, List[str]] = Field(default_factory=dict)

class ScheduleEntry(BaseModel):
    enabled: bool = True
    cron: str

class ScheduleConfig(BaseModel):
    daily_brief: ScheduleEntry | None = None
    media_digest: ScheduleEntry | None = None
    sys_digest: ScheduleEntry | None = None
    news_digest: ScheduleEntry | None = None
    gaming_digest: ScheduleEntry | None = None

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        extra="ignore",
        arbitrary_types_allowed=True,
    )

    GEMINI_API_KEY: str
    GEMINI_MODEL: str = 'gemini-1.5-flash'
    TELEGRAM_BOT_TOKEN: str | None = None
    TELEGRAM_CHAT_ID: str | None = None
    TZ: str = "UTC"

    BASE_DIR: Path = PROJECT_ROOT
    STATE_DIR: Path = PROJECT_ROOT / "state"

    daily: DailyConfig | None = None
    media: MediaConfig | None = None
    sys: SysConfig | None = None
    news: FeedBasedConfig | None = None
    gaming: FeedBasedConfig | None = None
    chat: Dict[str, Any] | None = None
    schedule: ScheduleConfig | None = None

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