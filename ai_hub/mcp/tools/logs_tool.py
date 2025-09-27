from __future__ import annotations
from typing import Any, Dict

from .base import ToolSpec

async def _exec_logs(app, args: Dict[str, Any]) -> str:
    return await app.dispatcher.run("logs.build")

TOOL = ToolSpec(
    name="logs_query",
    description=(
        "Fetch and summarize recent system/service logs into a clean Telegram digest. "
        "Use when the user asks for logs, errors, failures, or system status."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "level": {"type": "string", "description": "error|warning|info|debug"},
            "component": {"type": "string", "description": "service or component name"},
            "since": {"type": "string", "description": "ISO time or '1h'/'today'"},
            "limit": {"type": "integer", "minimum": 1, "maximum": 2000}
        },
        "additionalProperties": False,
    },
    execute=_exec_logs,
)