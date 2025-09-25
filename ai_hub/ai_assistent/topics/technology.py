import re
import textwrap
from .base import TopicHandler
from .utils import format_items_for_prompt, create_summary_instruction

class TechnologyDigestTopic(TopicHandler):
    def build_prompt(self, payload: dict) -> str:
        items = (payload.get("items") or [])
        count = payload.get("count")
        block = format_items_for_prompt(items)

        summary_instruction = create_summary_instruction(
            count,
            default="Write 5–8 short, high-signal items about technology (gadgets, software, industry news, startups)."
        )

        return textwrap.dedent(f"""
            You are a technology news editor. {summary_instruction}.
            Focus on concrete information: new product releases, major software updates, company milestones, and funding news.
            Avoid speculation and marketing buzzwords.

            OUTPUT FORMAT (STRICT):
            - Simple Markdown ONLY (no links, no code/quotes/tables).
            - Each item is exactly 2 lines:
              1) 💻 *Product or Company: News Headline* (≤ 80 chars)
              2) One-sentence summary (≤ 180 chars).
            - Put ONE blank line between items.

            Items to consider:
                {block}
        """).strip()

    def postprocess(self, llm_text: str) -> str:
        text = (llm_text or "").strip()
        if not text:
            return text

        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        blocks_raw = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]

        def trim(s: str, n: int) -> str:
            s = s.strip()
            return s if len(s) <= n else (s[: n - 1].rstrip() + "…")

        blocks = []
        for b in blocks_raw:
            lines = [ln.strip() for ln in b.splitlines() if ln.strip()]
            if not lines:
                continue

            title = lines[0]
            if "*" not in title:
                clean = re.sub(r"^\s*(?:[^\w\s]|💻)\s*", "", title)
                title = f"💻 *{clean}*"

            summary = lines[1] if len(lines) > 1 else ""

            title   = trim(title,   80)
            summary = trim(summary, 180)

            block = title if not summary else f"{title}\n{summary}"
            blocks.append(block)

        return "\n\n".join(blocks).strip()