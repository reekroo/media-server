from __future__ import annotations
from typing import List, Literal, Optional
from pydantic import BaseModel, Field
from datetime import datetime

Level = Literal["OK", "WARN", "FAIL"]

class UnitStatus(BaseModel):
    unit: str
    active: str
    restarts: int = 0
    fragment_path: Optional[str] = None

class LogEntry(BaseModel):
    ts: Optional[str] = None
    priority: Optional[str] = None
    line: str

class Issue(BaseModel):
    category: str
    pattern: str

class UnitReport(BaseModel):
    unit: str
    status: UnitStatus
    level: Level
    issues: List[Issue] = Field(default_factory=list)
    samples: List[str] = Field(default_factory=list)

class Incident(BaseModel):
    id: str
    unit: str
    level: Level
    reason: List[Issue] = Field(default_factory=list)
    restarts: int = 0
    active: str
    samples: List[str] = Field(default_factory=list)

class DigestSummary(BaseModel):
    ts: str = Field(default_factory=lambda: datetime.now().isoformat())
    lookback: str
    min_priority: str
    overall: Level
    reports: List[UnitReport]