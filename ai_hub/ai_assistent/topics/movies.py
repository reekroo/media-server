from __future__ import annotations
import textwrap
from .base import TopicHandler

class MoviesRecommend(TopicHandler):
    def build_prompt(self, payload: dict) -> str:
        titles = list(payload.get("titles") or [])
        prefs = dict(payload.get("prefs") or {})

        prefs_txt = ", ".join(f"{k}={v}" for k, v in prefs.items() if v)
        title_block = "\n".join(f"- {t}" for t in titles)

        return textwrap.dedent(f"""
            You are a senior movie curator. Use ONLY the user's LOCAL LIBRARY below.
            Produce a concise, Telegram-friendly recommendation digest.

            HARD RULES (STRICT):
            - Simple Markdown ONLY (no HTML, no code fences).
            - Organize into 2–4 thematic groups with *bold* group titles.
            - Each item is ONE line: Title — very short reason (<= 120 chars).
            - No duplicates. Do NOT repeat titles inside or across groups.
            - Do NOT include technical suffixes (WEB-DL, 1080p, x264, release tags) in titles.
            - Prefer variety: mix of new-to-start, hidden gems, and quick-watch picks.
            - One blank line between groups only (NOT between list items).
            
            Preferences: {prefs_txt if prefs_txt else "none"}
            Local Library (source list):
            {title_block}

            To conclude, add a final line starting with *Today's top:* and feature the one movie from the library you consider the most essential watch. 
            Do not repeat titles already listed in the groups above.
        """).strip()

    def postprocess(self, llm_text: str) -> str:
        return (llm_text or "").strip()