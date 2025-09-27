from pydantic import BaseModel
from typing import Optional

class MessageTargetConfig(BaseModel):
    enabled: bool = True
    to: str = "telegram"
    destination_group: str = ""
    destination_topic: Optional[str] = None
    destination_language: Optional[str] = None