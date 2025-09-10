from typing import Dict, List
from pydantic import BaseModel, Field

class FeedBasedConfig(BaseModel):
    enabled: bool = True
    max_items: int = 25
    feeds: Dict[str, List[str]] = Field(default_factory=dict)
