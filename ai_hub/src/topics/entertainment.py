from __future__ import annotations
from .base import TopicHandler
from ..common.feed_collector import FeedItem
import textwrap

class EntertainmentDigestTopic(TopicHandler):
    def build_prompt(self, payload: dict) -> str:
        items = [FeedItem(**item) for item in payload.get("items", [])]
        item_lines = [f"- {item.title}: {item.summary}" for item in items]
        block = "\n".join(item_lines)

        return textwrap.dedent(f"""
            You are a film and TV critic for a modern magazine.
            From the news items below, create a concise and engaging digest about what's new and upcoming.

            IMPORTANT: Format your response using simple Markdown. Use asterisks for bold section titles (*Movies*).

            Focus on:
            1. Major new releases (movies and TV series).
            2. Significant trailers or announcements.
            3. Interesting casting news.

            Structure your output into two short sections: *Movies* and *TV/Series*.
            Keep it brief, witty, and to the point.

            News Items:
                {block}
        """).strip()

    def postprocess(self, llm_text: str) -> str:
        return (llm_text or "").strip()