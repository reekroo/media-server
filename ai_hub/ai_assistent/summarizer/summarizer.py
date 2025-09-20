from __future__ import annotations
import json
import logging
import re

from ..agents.base import Agent
from .base import Summarizer

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

class SdkSummarizer(Summarizer):
    _PROMPT = """You are an assistant that produces a SHORT, POLICY-SAFE summary
        for use as an image generation prompt.

        Guidelines:
        - Output: one neutral sentence in English (max {max_chars} characters).
        - No people, no logos, no brands, no sensitive/explicit content.
        - Prefer abstract nouns, simple neutral concepts.
        - Style: descriptive, editorial, abstract-friendly.
        - No hashtags, mentions, URLs, emojis, markdown.

        Respond ONLY with a JSON object inside a markdown block:
        ```json
        {{
        "summary": "<safe prompt>"
        }}
        ```

        Input text:
        {text}
    """

    def __init__(self, agent: Agent):
        self._agent = agent

    async def summarize_for_image(self, text: str, max_chars: int = 220) -> str:
        original_text = (text or "").strip()
        if not original_text:
            return ""

        prompt = self._PROMPT.format(max_chars=max_chars, text=original_text)

        try:
            raw_response = await self._agent.generate(prompt)
            
            data = _parse_json_from_string(raw_response)
            if data and "summary" in data:
                summary = data["summary"].strip()
                if summary:
                    return summary[:max_chars]

            log.warning(
                "Summarization response was valid, but did not contain a 'summary' key.",
                extra={"raw_response": raw_response}
            )

        except Exception as e:
            log.error(
                "Summarization failed due to an exception. Falling back to original text.",
                exc_info=e,
                extra={"original_text": original_text}
            )

        return original_text.replace("\n", " ")[:max_chars]