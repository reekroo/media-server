from __future__ import annotations
import asyncio
import json
from typing import Any, Dict
from .base import Translator
from ...agents.base import Agent

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
        "- Keep ALL formatting and syntax EXACTLY as in input:\n"
        "  * Markdown / MarkdownV2 markers stay as-is (*, _, __, **, ``` code fences, `inline` code).\n"
        "  * HTML tags (<b>, <i>, <a href=...>, etc.) must remain intact.\n"
        "  * Links: keep the structure `[text](url)` or `<a href=\"...\">text</a>`; translate ONLY visible text, NEVER the URL.\n"
        "  * Mentions, hashtags, and emojis MUST remain unchanged (e.g., @user, #topic, 😊).\n"
        "  * Placeholders/tokens MUST remain unchanged (e.g., {name}, {{name}}, %s, {}, {{}}, {{.}}).\n"
        "  * Code blocks and inline code MUST NOT be translated or reformatted.\n"
        "- DO NOT add or remove backslashes or any escape characters.\n"
        "- DO NOT reflow paragraphs or merge/split lines; retain exact whitespace and newlines.\n"
        "- DO NOT add commentary, notes, quotes, or explanations.\n\n"
        "OUTPUT CONTRACT:\n"
        "Return STRICT JSON ONLY (no prose), with fields:\n"
        "{\n"
        '  "text": "<translated or original>",\n'
        '  "changed": true or false\n'
        "}\n\n"
        "Context:\n"
        "- target_lang: <<TARGET_LANG>>\n"
        "INPUT:\n"
    )

    def __init__(self, agent: Agent):
        self._agent = agent

    @staticmethod
    def _extract_json(s: str) -> Dict[str, Any]:
        first, last = s.find("{"), s.rfind("}")
        if first == -1 or last == -1 or last < first:
            return {}
        chunk = s[first:last + 1]
        for c in (chunk, chunk.replace("'", '"')):
            try:
                return json.loads(c)
            except Exception:
                continue
        return {}

    async def translate(self, text: str, target_lang: str) -> str:
        if not text:
            return text

        prompt = self._PROMPT_HEADER.replace("<<TARGET_LANG>>", str(target_lang)) + text
        try:
            raw = await self._agent.generate(prompt)
            raw = (raw or "").strip()
            if not raw:
                return text
            data = self._extract_json(raw)
            out = data.get("text") if isinstance(data.get("text"), str) else None
            changed = data.get("changed")
            if isinstance(changed, (str, int)):
                changed = str(changed).lower() in ("1", "true", "yes")
            if not isinstance(changed, bool):
                changed = (out or "") != text
            return out if (out and changed) else text
        except Exception:
            return text
