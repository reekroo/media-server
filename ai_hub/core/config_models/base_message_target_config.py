from typing import Optional

from .base_digest_config import BaseDigestConfig

class MessageTargetConfig(BaseDigestConfig):
    to: str = "telegram"
    destination_group: str = ""
    destination_topic: Optional[str] = None
    destination_language: Optional[str] = None