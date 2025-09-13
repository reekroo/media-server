from __future__ import annotations
import textwrap

from .base import TopicHandler
from .utils import format_items_for_prompt

class NewsDigestTopic(TopicHandler):
    def build_prompt(self, payload: dict) -> str:
        items = payload.get("items", [])[:30]
        section = payload.get("section", "news")
        block = format_items_for_prompt(items)

        return textwrap.dedent(f"""
            You are an editor for a morning {section} briefing. Summarize the items below into 5–10 bullets.
            
            IMPORTANT, OUTPUT FORMAT (STRICT):
            - Use simple Markdown ONLY (no HTML, no code fences).
            - Use asterisks for bold section titles (*Title*).
            - Put ONE blank line between items.

            Focus on what changed, why it matters, and what's next.
            Avoid clickbait; be precise; group related items.

            Items:
                {block}
        """).strip()

    def postprocess(self, llm_text: str) -> str:
        return (llm_text or "").strip()