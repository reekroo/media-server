import textwrap

from .base import TopicHandler
from .formatters.base import Formatter
from .formatters.markdown_digest_formatter import MarkdownDigestFormatter
from .utils import format_items_for_prompt, create_summary_instruction

class ScienceDigestTopic(TopicHandler):
    @property
    def formatter(self) -> Formatter:
        return MarkdownDigestFormatter()

    def build_prompt(self, payload: dict) -> str:
        items = (payload.get("items") or [])
        count = payload.get("count")
        block = format_items_for_prompt(items)

        summary_instruction = create_summary_instruction(
            count,
            default="Write 5–7 short, high-signal items about science news (discoveries, research, space exploration)."
        )

        return textwrap.dedent(f"""
            You are a science news editor for a broad audience. {summary_instruction}.
            Focus on the essence of the discovery: what was found, where, and why it is important.
            Avoid jargon and overly technical details.

            OUTPUT FORMAT (STRICT):
            - Simple Markdown ONLY (no links, no code/quotes/tables).
            - Each item is exactly 2 lines:
              1) *Field: Brief Title of Discovery* (≤ 80 chars)
              2) One-sentence summary (≤ 180 chars). Mention the research source if relevant.
            - Put ONE blank line between items.

            Items to consider:
                {block}
        """).strip()