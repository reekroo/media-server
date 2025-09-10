from typing import List
from pydantic import BaseModel, Field

class MediaRecommenderConfig(BaseModel):
    language: str = "en"
    genres: List[str] = Field(default_factory=list)