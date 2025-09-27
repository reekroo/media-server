from typing import List, Optional
from pathlib import Path
from pydantic import Field

from .media_recommender_config import MediaRecommenderConfig
from .message_target_config import MessageTargetConfig

class MediaConfig(MessageTargetConfig):
    generate_image: Optional[bool] = False
    
    max_depth: int = 6
    root: Path = Path("/mnt/storage/media")
    state_path: str = "state/media_index.json"
    include_ext: List[str] = Field(default_factory=lambda: [".mkv", ".mp4"])

    recommender: MediaRecommenderConfig = Field(default_factory=MediaRecommenderConfig)