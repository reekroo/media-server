from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class FeedBasedConfig(BaseModel):
    enabled: bool = True
    max_items: int = 25
    to: str = "telegram"
    destination: str = ""
    destination_language: Optional[str] = None
    
    ai_topic: str = ""
    render_template: str = "{summary}"
    feeds: Dict[str, List[str]] = Field(default_factory=dict)