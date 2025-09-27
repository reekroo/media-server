import textwrap

from .base import TopicHandler
from .formatters.base import Formatter
from .formatters.markdown_digest_formatter import MarkdownDigestFormatter
from .utils import format_items_for_prompt, create_summary_instruction

class CultureDigestTopic(TopicHandler):
    @property
    def formatter(self) -> Formatter:
        return MarkdownDigestFormatter()

    def build_prompt(self, payload: dict) -> str:
        items = payload.get("items", [])[:30]
        count = payload.get("count")
        block = format_items_for_prompt(items)

        summary_instruction = create_summary_instruction(
            count,
            default="Write 5–7 short, high-signal items about arts and culture (exhibitions, books, music, theater)."
        )

        return textwrap.dedent(f"""
            You are an arts and culture editor. {summary_instruction}.
            Focus on significant events: major exhibition openings, notable book releases, important premieres, and cultural awards.
            Be concise and informative.

            OUTPUT FORMAT (STRICT):
            - Simple Markdown ONLY (no links, no code/quotes/tables).
            - Each item is exactly 2 lines:
              1) *Field: Title or Event Name* (≤ 80 chars)
              2) One-sentence summary (≤ 180 chars). Mention location/date if relevant.
            - Put ONE blank line between items.

            Items to consider:
                {block}
        """).strip()