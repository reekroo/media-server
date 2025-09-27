from __future__ import annotations
from typing import Any, Dict

from .base import ToolSpec

async def _exec_media(app, args: Dict[str, Any]) -> str:
    return await app.dispatcher.run("media.build", config_name="media")

TOOL = ToolSpec(
    name="media_digest",
    description=(
        "Summarize new media additions and provide tailored viewing suggestions "
        "based on stored preferences. Use when the user asks about new movies/shows "
        "or wants recommendations."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {},
        "additionalProperties": False,
    },
    execute=_exec_media,
)