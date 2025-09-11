from typing import Dict, List
from pydantic import BaseModel, Field

class FeedBasedConfig(BaseModel):
    enabled: bool = True
    max_items: int = 25
    to: str = "telegram"
    destination: str = ""
    ai_topic: str = ""
    render_template: str = "{summary}"
    feeds: Dict[str, List[str]] = Field(default_factory=dict)