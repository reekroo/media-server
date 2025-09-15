from __future__ import annotations
from typing import Any, Dict

from .base import ToolSpec
from mcp.rpc_methods.dinner import build_digest

async def _exec_dinner(app, args: Dict[str, Any]) -> str:
    return await build_digest(app, config_name="dinner")

TOOL = ToolSpec(
    name="dinner_get",
    description=(
        "Generate a concise dinner ideas digest based on user's stored preferences "
        "(cuisine, excluded ingredients, prep/cook times). Use when the user asks for dinner ideas."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    },
    execute=_exec_dinner,
)
