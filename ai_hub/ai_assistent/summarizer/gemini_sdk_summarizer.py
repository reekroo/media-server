from __future__ import annotations
import json

from ..agents.base import Agent

class SdkSummarizer:
    _PROMPT = """You are an assistant that produces a SHORT, POLICY-SAFE summary
        for use as an image generation prompt.

        Guidelines:
        - Output: one neutral sentence in English (max {max_chars} characters).
        - No people, no logos, no brands, no sensitive/explicit content.
        - Prefer abstract nouns, simple neutral concepts.
        - Style: descriptive, editorial, abstract-friendly.
        - No hashtags, mentions, URLs, emojis, markdown.

        Respond ONLY with JSON:
        {{
        "summary": "<safe prompt>"
        }}

        Input text:
        {text}
    """

    def __init__(self, agent: Agent):
        self._agent = agent

    async def summarize_for_image(self, text: str, max_chars: int = 220) -> str:
        if not text:
            return ""

        prompt = self._PROMPT.format(max_chars=max_chars, text=text)

        try:
            raw = await self._agent.generate(prompt)
            data = json.loads(raw[raw.find("{"): raw.rfind("}") + 1])
            summary = data.get("summary", "").strip()
            if summary:
                return summary[:max_chars]
        except Exception:
            pass

        return text.strip().replace("\n", " ")[:max_chars]
