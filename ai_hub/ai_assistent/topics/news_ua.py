from __future__ import annotations
import textwrap

from .base import TopicHandler
from functions.feeds.feed_collector import FeedItem

class UkraineNewsDigestTopic(TopicHandler):
    def build_prompt(self, payload: dict) -> str:
        items = [FeedItem(**item) for item in payload.get("items", [])]
        section = payload.get("section", "news")

        item_lines = [f"- {item.title}: {item.summary}" for item in items]
        block = "\n".join(item_lines)

        return textwrap.dedent(f"""
            You are a news editor summarizing news from Ukraine.
            Analyze the following news items from Ukrainian sources on the topic of '{section}'.
            Your final summary MUST be in Ukrainian.

            IMPORTANT, OUTPUT FORMAT (STRICT):
            - Use simple Markdown ONLY (no HTML, no code fences).
            - Use asterisks for bold section titles (*Назва розділу*).
            - Put ONE blank line between items.

            Create 5-10 concise bullets focusing on the most important events, what changed, and why it matters.

            News Items (from Ukraine):
                {block}
        """).strip()

    def postprocess(self, llm_text: str) -> str:
        return (llm_text or "").strip()