from typing import List
from pydantic import BaseModel, Field

from .sys_patterns_config import SysPatternsConfig

class SysConfig(BaseModel):
    enabled: bool = True
    lookback: str = "24h"
    min_priority: str = "warning"
    max_restarts: int = 3
    to: str = "telegram"
    destination: str = ""
    units: List[str] = Field(default_factory=list)
    patterns: SysPatternsConfig = Field(default_factory=SysPatternsConfig)