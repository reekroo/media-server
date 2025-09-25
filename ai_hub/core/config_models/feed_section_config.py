from typing import List
from pydantic import BaseModel, Field

class FeedSectionConfig(BaseModel):
    urls: List[str] = Field(default_factory=list)
    fetch_limit: int = 25
    section_limit: int = 3