from __future__ import annotations
from typing import Any, Dict

from .base import ToolSpec
from mcp.rpc_methods.dinner import build_digest

_MIN, _MAX, _DEFAULT = 1, 5, 3

def _normalize_count(value: Any) -> int | None:
    try:
        if value is None:
            return None
        n = int(value)
        if n < _MIN: n = _MIN
        if n > _MAX: n = _MAX
        return n
    except Exception:
        return None

async def _exec_dinner(app, args: Dict[str, Any]) -> str:
    count = _normalize_count(args.get("count"))
    return await build_digest(app, config_name="dinner", count=count)

TOOL = ToolSpec(
    name="dinner_get",
    description=(
        "Generate a concise dinner-ideas digest using user's stored preferences "
        "(cuisine, exclusions, prep/cook time)."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "count": {
                "type": "integer",
                "minimum": _MIN,
                "maximum": _MAX,
                "description": f"How many dinner ideas to generate (default {_DEFAULT}).",
            }
        },
        "additionalProperties": False,
    },
    execute=_exec_dinner,
)
