from typing import List, Optional
from pydantic import Field

from .sys_patterns_config import SysPatternsConfig
from .message_target_config import MessageTargetConfig

class SysConfig(MessageTargetConfig):    
    generate_image: Optional[bool] = False
    
    lookback: str = "24h"
    min_priority: str = "warning"
    max_restarts: int = 3
    
    units: List[str] = Field(default_factory=list)
    patterns: SysPatternsConfig = Field(default_factory=SysPatternsConfig)