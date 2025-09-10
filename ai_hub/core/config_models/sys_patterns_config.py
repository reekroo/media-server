from typing import List
from pydantic import BaseModel, Field

class SysPatternsConfig(BaseModel):
    disk: List[str] = Field(default_factory=list)
    net: List[str] = Field(default_factory=list)
    app: List[str] = Field(default_factory=list)