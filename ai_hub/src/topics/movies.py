from __future__ import annotations
import textwrap
from .base import TopicHandler

class MoviesRecommend(TopicHandler):
    def build_prompt(self, payload: dict) -> str:
        titles = list(payload.get("titles") or [])[:600]
        prefs = dict(payload.get("prefs") or {})
        prefs_txt = ", ".join(f"{k}={v}" for k, v in prefs.items())
        title_block = "\n".join(f"- {t}" for t in titles)
        
        return textwrap.dedent(f"""
            You are a movie curator. Based ONLY on the user's LOCAL LIBRARY list below,
            pick ~10 watch-next suggestions and group them.
            
            IMPORTANT: Format your response using simple Markdown. Use asterisks for bold (*bold text*). Do NOT use HTML tags.

            Preferences: {prefs_txt}

            Local Library:
            {title_block}

            Output requirements:
            - Use asterisks for group headings (e.g., *Epic Sci-Fi Sagas*).
            - Each line should be a list item: Title — one-line reason.
            - Finish with *Top Picks for Tonight:*.
        """).strip()

    def postprocess(self, llm_text: str) -> str:
        return (llm_text or "").strip()
