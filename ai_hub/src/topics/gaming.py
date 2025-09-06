from __future__ import annotations
import textwrap
from .base import TopicHandler

class GamingDigestTopic(TopicHandler):
    def build_prompt(self, payload: dict) -> str:
        # payload: {"items":[{"title":..., "summary":..., "link":...}, ...]}
        items = payload.get("items", [])[:30]
        lines = []
        for it in items:
            t = it.get("title","")
            s = it.get("summary","")
            lines.append(f"- {t} — {s}")
        block = "\n".join(lines)
        return textwrap.dedent(f"""
            You are a gaming news curator. Create 5–8 concise bullets for core updates (releases, patches, delays, trailers).
            - Keep it actionable (dates/platforms). Avoid hype.
            - Output plain text bullets only.
            
            Items:
            {block}
        """).strip()

    def postprocess(self, llm_text: str) -> str:
        return (llm_text or "").strip()
