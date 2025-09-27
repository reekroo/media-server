import textwrap

from .base import TopicHandler
from .formatters.base import Formatter
from .formatters.markdown_news_formatter import MarkdownNewsFormatter
from .utils import format_items_for_prompt, create_summary_instruction

class NewsDigestTopic(TopicHandler):
    @property
    def formatter(self) -> Formatter:
        return MarkdownNewsFormatter()

    def build_prompt(self, payload: dict) -> str:
        items   = (payload.get("items") or [])
        section = payload.get("section") or "news"
        count   = payload.get("count")

        block = format_items_for_prompt(items)
        qty = create_summary_instruction(count)

        return textwrap.dedent(f"""
            You are an editor for a {section} briefing. {qty}
            Focus on what changed, why it matters, and what's next. Avoid clickbait.

            OUTPUT FORMAT (STRICT):
            - Simple Markdown ONLY (no links, no code, no tables).
            - Each item is exactly 2 lines:
              1) *Title*  (≤ 70 chars)
              2) One-sentence summary (≤ 260 chars).
            - Put ONE blank line between items. No bullets, no numbering.
            - Group related facts into a single item when sensible.

            Source items:
                {block}
        """).strip()