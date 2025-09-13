from __future__ import annotations
import textwrap

from .base import TopicHandler
from .utils import format_items_for_prompt

class GamingDigestTopic(TopicHandler):
    def build_prompt(self, payload: dict) -> str:
        items = payload.get("items", [])[:30]
        block = format_items_for_prompt(items)
        
        return textwrap.dedent(f"""
            You are a gaming news curator. Create 5–10 concise bullets for core updates (releases, patches, delays, trailers).
          
            IMPORTANT, OUTPUT FORMAT (STRICT):
            - Use simple Markdown ONLY (no HTML, no code fences).
            - Use asterisks for bold section titles (*Title*).
            - Put ONE blank line between items.
                               
            Keep it actionable (dates/platforms). Avoid hype.
            
            Items:
                {block}
        """).strip()

    def postprocess(self, llm_text: str) -> str:
        return (llm_text or "").strip()