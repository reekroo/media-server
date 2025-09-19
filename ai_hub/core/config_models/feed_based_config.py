from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class FeedBasedConfig(BaseModel):
    enabled: bool = True
    to: str = "telegram"
    destination: str = ""
    destination_topic: Optional[str] = None
    destination_language: Optional[str] = None
    generate_image: Optional[bool] = True
    
    max_items: int = 25
    ai_topic: str = ""
    render_template: str = "{summary}"
    feeds: Dict[str, List[str]] = Field(default_factory=dict)