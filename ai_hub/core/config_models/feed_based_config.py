from typing import Dict, Optional
from pydantic import BaseModel, Field

from .feed_section_config import FeedSectionSettings

class FeedBasedConfig(BaseModel):
    enabled: bool = True
    to: str = "telegram"
    destination_group: str = ""
    destination_topic: Optional[str] = None
    destination_language: Optional[str] = None
    
    ai_topic: str = ""
    
    feeds: Dict[str, FeedSectionSettings] = Field(default_factory=dict)