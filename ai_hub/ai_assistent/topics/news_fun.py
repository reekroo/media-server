import textwrap
from .base import TopicHandler
from .utils import format_items_for_prompt, create_summary_instruction

class FunNewsDigestTopic(TopicHandler):
    def build_prompt(self, payload: dict) -> str:
        items = payload.get("items", [])
        count = payload.get("count")
        
        block = format_items_for_prompt(items)
        summary_instruction = create_summary_instruction(
            count,
            default="Create 5-7 of these 'news stories'"
        )

        return textwrap.dedent(f"""
            You are a satirical columnist (Onion-style). Create humorous, anecdotal mini-stories
            inspired by the real news below. These are FICTION and jokes, not factual reporting.
            Dark humor is allowed in moderation.
                               
            BOUNDARIES:
            - Do NOT include hate speech, slurs, or target protected classes.
            - No defamation of real private individuals. Avoid explicit criminal accusations.
            - No instructions for wrongdoing; avoid celebrating real harm or tragedy.
            - Base each joke on the provided items (names, places, facts) but transform it into satire.

            OUTPUT FORMAT (STRICT, Simple Markdown only — no links/code/tables/quotes):
            - Each item is ONE compact block with:
            1) *Satirical headline*  (≤ 70 chars)
            2) 1–2 short sentences as a punchline (≤ 220 chars total).
            - Put ONE blank line between items. No bullets, no numbering, no emojis.
            - Keep wording crisp; ensure the humorous intent is clear (fictional tone).

            {summary_instruction} based on the provided material.

            Inspiration material (real news to riff on):
            {block}
        """).strip()
    
    def postprocess(self, llm_text: str) -> str:
        import re
        text = (llm_text or "").strip()
        if not text:
            return text
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        text = "\n".join(ln.rstrip() for ln in text.splitlines())
        return text