from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict

ToolExec = Callable[["AppContext", Dict[str, Any]], Awaitable[str]]

@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    parameters_json_schema: Dict[str, Any]
    execute: ToolExec
