# core/config_models/feed_based_config.py

from typing import Dict, List
from pydantic import BaseModel, Field

class FeedBasedConfig(BaseModel):
    """
    Упрощенная модель для всех feed-based конфигов.
    Ожидает простую структуру в TOML:
    [feeds]
    general = ["url1", "url2"]
    tech = ["url3"]
    """
    enabled: bool = True
    max_items: int = 25
    to: str = "telegram"
    destination: str = ""
    ai_topic: str = ""
    render_template: str = "{summary}"
    feeds: Dict[str, List[str]] = Field(default_factory=dict)