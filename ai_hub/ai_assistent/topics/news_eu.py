import textwrap
import re

from .base import TopicHandler
from .utils import format_items_for_prompt, create_summary_instruction

class EuropeanNewsDigestTopic(TopicHandler):
    def build_prompt(self, payload: dict) -> str:
        items   = (payload.get("items") or [])
        section = payload.get("section") or "Europe"
        count   = payload.get("count")

        block = format_items_for_prompt(items)
        qty = create_summary_instruction(count)

        return textwrap.dedent(f"""
            You are an editor for a {section} briefing. Respond in English. {qty}
            Focus on what changed, why it matters, and what's next. Avoid clickbait.

            OUTPUT FORMAT (STRICT):
            - Simple Markdown ONLY (no links, no code, no tables).
            - Each item is exactly 2 lines:
              1) *Title*  (≤ 70 chars)
              2) One-sentence summary (≤ 260 chars). Add date/region if relevant.
            - Put ONE blank line between items. No bullets, no numbering.
            - Group related facts into a single item when sensible.

            Source items:
                {block}
        """).strip()

    def postprocess(self, llm_text: str) -> str:
        text = (llm_text or "").strip()
        if not text:
            return text
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        text = "\n".join(ln.rstrip() for ln in text.splitlines())
        return text
