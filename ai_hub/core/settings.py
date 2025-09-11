from __future__ import annotations
from pathlib import Path
import tomllib
import zoneinfo
from typing import Any, List, Dict, get_args

from pydantic import Field, model_validator, field_validator, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict

# Импортируем все наши Pydantic-модели и метаданные
from .config_models import (
    DailyConfig, DinnerConfig, MediaConfig, SysConfig, LogsConfig,
    FeedBasedConfig, ScheduleConfig, TomlMetadata
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # --- Переменные окружения ---
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = 'gemini-2.5-flash'
    TELEGRAM_BOT_TOKEN: str | None = None
    TELEGRAM_ADMIN_IDS: List[str] = Field(default_factory=list)
    TZ: str = Field(default="Europe/Istanbul")
    DEFAULT_LANG: str = "ru"

    # --- Директории ---
    BASE_DIR: Path = PROJECT_ROOT
    STATE_DIR: Path = PROJECT_ROOT / "state"

    # --- Декларативная загрузка конфигов из TOML ---
    # Мы "аннотируем" каждое поле метаданными о том, как его загрузить.
    # Имя поля (например, "daily") = имя файла ("daily.toml").
    schedule: ScheduleConfig | None = Field(default=None, json_schema_extra=TomlMetadata())
    daily:    DailyConfig    | None = Field(default=None, json_schema_extra=TomlMetadata())
    dinner:   DinnerConfig   | None = Field(default=None, json_schema_extra=TomlMetadata())
    media:    MediaConfig    | None = Field(default=None, json_schema_extra=TomlMetadata())
    sys:      SysConfig      | None = Field(default=None, json_schema_extra=TomlMetadata())
    logs:     LogsConfig     | None = Field(default=None, json_schema_extra=TomlMetadata())
    news:     FeedBasedConfig| None = Field(default=None, json_schema_extra=TomlMetadata())
    news_by:  FeedBasedConfig| None = Field(default=None, json_schema_extra=TomlMetadata())
    news_tr:  FeedBasedConfig| None = Field(default=None, json_schema_extra=TomlMetadata())
    gaming:   FeedBasedConfig| None = Field(default=None, json_schema_extra=TomlMetadata())
    entertainment: FeedBasedConfig| None = Field(default=None, json_schema_extra=TomlMetadata())

    @field_validator("TELEGRAM_ADMIN_IDS", mode='before')
    @classmethod
    def _parse_admin_ids(cls, v: Any) -> List[str]:
        """Преобразует строку или число в список строк."""
        if isinstance(v, str):
            return [item.strip() for item in v.split(',') if item.strip()]
        if isinstance(v, (int, float)):
            return [str(v)]
        return v or []

    @model_validator(mode='after')
    def _load_and_parse_toml_configs(self) -> 'Settings':
        config_dir = self.BASE_DIR / "configs"

        # 1. Итерируем по всем полям самой модели Settings
        for field_name, field_info in self.model_fields.items():
            # 2. Извлекаем наши метаданные
            metadata = field_info.json_schema_extra
            if not isinstance(metadata, TomlMetadata):
                continue

            # 3. Загружаем и парсим TOML по соглашению: имя поля = имя файла
            path = config_dir / f"{field_name}.toml"
            if not path.exists():
                continue
            
            try:
                data = tomllib.loads(path.read_text("utf-8"))

                # 4. Извлекаем нужный под-ключ (если указан в метаданных)
                if metadata.key:
                    data = data.get(metadata.key, {})
                
                # 5. Получаем тип поля (например, DailyConfig) из аннотации
                # get_args(T | None) -> (T,)
                model_class = get_args(field_info.annotation)[0]
                
                # 6. Создаем экземпляр Pydantic-модели и устанавливаем атрибут
                setattr(self, field_name, model_class(**data))

            except Exception as e:
                print(f"⚠️  Warning: Could not load or parse '{path.name}': {e}")
        
        # Пост-обработка путей
        if self.media and isinstance(self.media.state_path, str):
             self.media.state_path = self.STATE_DIR / Path(self.media.state_path).name
        if self.sys and isinstance(getattr(self.sys, 'state_path', None), str):
            self.sys.state_path = self.STATE_DIR / Path(self.sys.state_path).name

        return self