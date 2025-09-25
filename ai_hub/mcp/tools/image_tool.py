from __future__ import annotations
import base64
from typing import Any, Dict
from .base import ToolSpec

def _b64(img: bytes) -> str:
    return base64.b64encode(img).decode("ascii")

async def _exec_image(app, args: Dict[str, Any]) -> Dict[str, Any]:
    prompt: str = (args.get("prompt") or "").strip()
    if not prompt:
        prompt = "A simple abstract illustration"

    mode = (args.get("mode") or "prompt").strip().lower()
    if mode == "summary":
        img = await app.ai_service.generate_image_from_summary(prompt)
    else:
        img = await app.ai_service.generate_image_from_prompt(prompt)

    return {"mime": "image/png", "b64": _b64(img)}

TOOL = ToolSpec(
    name="image_generate",
    description=(
        "Generate one illustrative image from a natural-language description. "
        "Use when the user asks to generate/make/draw a picture."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "prompt": {"type": "string", "description": "What to draw."},
            "mode": {
                "type": "string",
                "enum": ["prompt", "summary"],
                "description": "Use 'prompt' for direct description (default) or 'summary' for short synopsis.",
            },
        },
        "required": ["prompt"],
        "additionalProperties": False,
    },
    execute=_exec_image,
)
