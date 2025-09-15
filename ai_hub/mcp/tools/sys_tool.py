from __future__ import annotations
from typing import Any, Dict

from .base import ToolSpec
from mcp.rpc_methods.sys import build_digest

async def _exec_sys(app, args: Dict[str, Any]) -> str:
    return await build_digest(app, config_name="sys")

TOOL = ToolSpec(
    name="sys_digest",
    description=(
        "Get a summarized system health digest (services status, recent critical logs, "
        "incidents). Use when the user asks about system status/health/errors."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    },
    execute=_exec_sys,
)
