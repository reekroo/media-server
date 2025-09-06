from __future__ import annotations
import textwrap, json
from .base import TopicHandler

class NewsDigestTopic(TopicHandler):
    def build_prompt(self, payload: dict) -> str:
        # payload: {"items":[{"title":..., "summary":..., "link":...}, ...], "section":"general"}
        items = payload.get("items", [])[:30]
        section = payload.get("section", "news")
        lines = []
        for it in items:
            t = it.get("title","")
            s = it.get("summary","")
            lines.append(f"- {t} — {s}")
        block = "\n".join(lines)
        return textwrap.dedent(f"""
            You are an editor for a morning {section} briefing. Summarize the items below into 5–8 bullets:
            - Focus on what changed, why it matters, and what's next.
            - Avoid clickbait; be precise; group related items.
            - Output plain text bullets, optionally with short sub-bullets.
            
            Items:
            {block}
        """).strip()

    def postprocess(self, llm_text: str) -> str:
        return (llm_text or "").strip()
