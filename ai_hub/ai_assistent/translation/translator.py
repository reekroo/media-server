from __future__ import annotations
import json
import logging
import re

from .base import Translator
from ..agents.base import Agent

log = logging.getLogger(__name__)

def _parse_json_from_string(text: str) -> dict | None:
    match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            log.warning("Found a JSON markdown block, but failed to parse its content.")
    
    match = re.search(r"(\{.*?\})", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            log.warning("Found a raw JSON-like string, but failed to parse it.")

    return None

class SdkTranslator(Translator):
    _PROMPT_HEADER = (
        "You are a STRICT translation executor for an outbound message pipeline.\n"
        "Goal: produce user-facing text in the TARGET language while PRESERVING FORMATTING EXACTLY.\n"
        "Decide nothing beyond translation.\n\n"
        "Targeting:\n"
        "- The TARGET language is provided below as `target_lang`.\n"
        "- Detect the SOURCE language automatically.\n"
        "- If SOURCE == TARGET → return the input text UNCHANGED.\n\n"
        "STRICT PRESERVATION RULES (MANDATORY):\n"
        "- We use SIMPLE MARKDOWN (NOT MarkdownV2). Keep ALL Markdown markers as-is (*, _, __, **, ``` code fences, `inline`).\n"
        "- BULLETS: If a line starts with \"- \" (hyphen + space), keep EXACTLY \"- \" at the start. "
        "Never replace '-' with typographic dashes (–, —) or bullets (•), and never change spacing.\n"
        "- Do NOT add or remove backslashes or any escape characters.\n"
        "- Do NOT reflow paragraphs or merge/split lines; retain exact whitespace and newlines.\n"
        "- Links: keep the structure `[text](url)`; translate ONLY visible text, NEVER the URL.\n"
        "- Mentions, hashtags, emojis, placeholders/tokens (e.g., {name}, {{name}}) MUST remain unchanged.\n"
        "- Code blocks and inline code MUST NOT be translated or reformatted.\n"
        "- DO NOT add commentary, notes, quotes, or explanations.\n\n"
        "OUTPUT CONTRACT:\n"
        "Return a JSON object inside a markdown block with fields:\n"
        "```json\n"
        "{\n"
        '  "text": "<translated or original>",\n'
        '  "changed": true or false\n'
        "}\n"
        "```\n\n"
        "Context:\n"
        "- target_lang: <<TARGET_LANG>>\n"
        "INPUT:\n"
    )

    def __init__(self, agent: Agent):
        self._agent = agent

    async def translate(self, text: str, target_lang: str) -> str:
        original_text = (text or "").strip()
        if not original_text:
            return ""

        prompt = self._PROMPT_HEADER.replace("<<TARGET_LANG>>", str(target_lang)) + original_text
        
        try:
            raw_response = await self._agent.generate(prompt)
            if not raw_response:
                return original_text
            
            data = _parse_json_from_string(raw_response)
            
            if not isinstance(data, dict):
                log.warning(
                    "Failed to parse JSON from translator response. Falling back to original text.",
                    extra={"raw_response": raw_response}
                )
                return original_text

            translated_text = data.get("text")

            if not isinstance(translated_text, str):
                return original_text

            was_changed = data.get("changed", False) is True

            if translated_text and was_changed:
                return translated_text

            return original_text

        except Exception as e:
            log.error(
                "Translation failed due to an exception. Falling back to original text.",
                exc_info=e,
                extra={"original_text": original_text, "target_lang": target_lang}
            )
            return original_text