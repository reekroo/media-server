from __future__ import annotations
from typing import Any, Dict

from .base import ToolSpec
from mcp.rpc_methods.daily import build_brief

async def _exec_daily(app, args: Dict[str, Any]) -> str:
    return await build_brief(app, config_name="daily")

TOOL = ToolSpec(
    name="daily_brief",
    description=(
        "Compose a concise daily brief including local weather and, if configured, "
        "recent earthquakes. Use when the user asks for a daily summary/brief."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    },
    execute=_exec_daily,
)
