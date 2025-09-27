import textwrap

from .base import TopicHandler
from .formatters.base import Formatter
from .formatters.markdown_digest_formatter import MarkdownDigestFormatter
from .utils import format_items_for_prompt, create_summary_instruction

class TechnologyDigestTopic(TopicHandler):
    @property
    def formatter(self) -> Formatter:
        return MarkdownDigestFormatter()

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
              1) *Product or Company: News Headline* (≤ 80 chars)
              2) One-sentence summary (≤ 180 chars).
            - Put ONE blank line between items.

            Items to consider:
                {block}
        """).strip()