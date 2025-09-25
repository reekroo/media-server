from __future__ import annotations
from typing import Any, Dict

from .base import ToolSpec
from ..rpc_methods import assist 

async def _exec_translate(app, args: Dict[str, Any]) -> str:
    target_lang = args.get("target_lang")
    text = args.get("text")
    
    if not target_lang or not text:
        return "Error: Both 'target_lang' and 'text' are required."

    return await assist.translate(app, target_lang=target_lang, text=text)

TOOL = ToolSpec(
    name="text_translator",
    description=(
        "Translates a given text to a specified target language. "
        "Use this if the user explicitly asks to translate something."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "target_lang": {
                "type": "string",
                "description": "The target language for the translation, specified as a 2-letter code (e.g., 'en', 'ru', 'tr')."
            },
            "text": {
                "type": "string",
                "description": "The text to be translated."
            }
        },
        "required": ["target_lang", "text"],
        "additionalProperties": False,
    },
    execute=_exec_translate,
)