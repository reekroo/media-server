from __future__ import annotations
from typing import Any, Dict
from .base import ToolSpec

async def _exec_image(app, args: Dict[str, Any]) -> Dict[str, Any]:
    prompt: str = (args.get("prompt") or "").strip()
    if not prompt:
        prompt = "A simple abstract illustration"

    mode = (args.get("mode") or "prompt").strip().lower()
    
    if mode == "summary":
        rpc_method_name = "assist.generate_image_b64_from_summary"
    else:
        rpc_method_name = "assist.generate_image_b64_from_prompt"
        
    return await app.dispatcher.run(rpc_method_name, text_summary=prompt)

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