from typing import List
from pathlib import Path
from pydantic import BaseModel, Field

from media_recommender_config import MediaRecommenderConfig

class MediaConfig(BaseModel):
    enabled: bool = True
    root: Path = Path("/mnt/storage/media")
    max_depth: int = 6
    include_ext: List[str] = Field(default_factory=lambda: [".mkv", ".mp4"])
    state_path: Path
    recommender: MediaRecommenderConfig = Field(default_factory=MediaRecommenderConfig)