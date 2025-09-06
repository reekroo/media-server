from __future__ import annotations
from .base import TopicHandler
from ..common.feed_collector import FeedItem
import textwrap

class TurkishNewsDigestTopic(TopicHandler):
    def build_prompt(self, payload: dict) -> str:
        items = [FeedItem(**item) for item in payload.get("items", [])]
        section = payload.get("section", "news")

        item_lines = [f"- {item.title}: {item.summary}" for item in items]
        block = "\n".join(item_lines)

        return textwrap.dedent(f"""
            You are a news editor summarizing Turkish news for an international audience.
            Analyze the following news items from Turkish sources on the topic of '{section}'.
            Your final summary MUST be in English.

            Create 5-8 concise bullets focusing on the most important events, what changed, and why it matters.

            News Items (in Turkish):
            {block}
        """).strip()

    def postprocess(self, llm_text: str) -> str:
        return (llm_text or "").strip()