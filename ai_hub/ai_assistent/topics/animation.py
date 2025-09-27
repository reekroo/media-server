import textwrap

from .base import TopicHandler
from .formatters.base import Formatter
from .formatters.markdown_digest_formatter import MarkdownDigestFormatter
from .utils import format_items_for_prompt, create_summary_instruction

class AnimationDigestTopic(TopicHandler):
    @property
    def formatter(self) -> Formatter:
        return MarkdownDigestFormatter()

    def build_prompt(self, payload: dict) -> str:
        items = (payload.get("items") or [])
        count = payload.get("count")

        block = format_items_for_prompt(items)
        summary_instruction = create_summary_instruction(
            count,
            default="Write 5–7 short, high-signal items about animation (series, movies, trailers, studios)."
        )

        return textwrap.dedent(f"""
            You are a curator of news about animation and anime. {summary_instruction}.
            Focus on facts: titles, release dates, studio announcements, and new trailers.
            Avoid rumors and long reviews.

            OUTPUT FORMAT (STRICT):
            - Simple Markdown ONLY (no links, no code/quotes/tables).
            - Each item is exactly 2 lines:
              1) *Title of Series or Movie* (≤ 80 chars)
              2) One-sentence summary (≤ 180 chars). Mention date/platform if relevant.
            - Put ONE blank line between items.

            Items to consider:
                {block}
        """).strip()