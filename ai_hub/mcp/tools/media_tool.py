from __future__ import annotations
from typing import Any, Dict

from .base import ToolSpec
from mcp.rpc_methods.media import build_digest

async def _exec_media(app, args: Dict[str, Any]) -> str:
    return await build_digest(app, config_name="media")

TOOL = ToolSpec(
    name="media_digest",
    description=(
        "Summarize new media additions and provide tailored viewing suggestions "
        "based on stored preferences. Use when the user asks about new movies/shows "
        "or wants recommendations."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            # future: {"limit": {"type": "integer", "minimum": 1, "maximum": 50}}
        },
        "additionalProperties": False,
    },
    execute=_exec_media,
)
