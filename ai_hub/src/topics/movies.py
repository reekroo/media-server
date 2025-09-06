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
            pick ~10 watch-next suggestions and group them (e.g., mood, genre, classics, new-to-watch).
            Do NOT recommend titles that are not present in the list. If duplicates/remuxes exist,
            suggest the best version.

            Preferences: {prefs_txt}

            Local Library:
            {title_block}

            Output:
            - 2–3 short groups; each line: Title — one-line reason
            - Finish with 1–2 top picks for tonight
        """).strip()
    def postprocess(self, llm_text: str) -> str:
        return (llm_text or "").strip()
