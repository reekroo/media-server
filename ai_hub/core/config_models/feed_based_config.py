from typing import Dict, Optional
from pydantic import Field

from .feed_section_config import FeedSectionSettings
from .message_target_config import MessageTargetConfig

class FeedBasedConfig(MessageTargetConfig):
    ai_topic: str = ""
    feeds: Dict[str, FeedSectionSettings] = Field(default_factory=dict)