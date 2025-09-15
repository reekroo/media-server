from __future__ import annotations
import textwrap

from .base import TopicHandler
from functions.feeds.feed_collector import FeedItem

class FunNewsDigestTopic(TopicHandler):
    def build_prompt(self, payload: dict) -> str:
        items = [FeedItem(**item) for item in payload.get("items", [])]
        
        item_lines = [f"- {item.title}: {item.summary}" for item in items]
        block = "\n".join(item_lines)

        return textwrap.dedent(f"""
            You are a stand-up comedian and satirist who writes a fake news column in the style of "The Onion".
            Your task is to take REAL news headlines and their summaries, and based on them, invent entirely new, absurd, funny, or pun-filled news stories.
            You must present them with a completely serious tone, as if they were real events.

            IMPORTANT: Do not just retell or summarize the real news. Use it as a springboard for your imagination. Take a fact, a name, or a situation and invent a funny, anecdotal story based on it. Your goal is to make the reader laugh.

            OUTPUT FORMAT REQUIREMENTS (STRICT):
            - Your final summary MUST be in English.
            - Use simple Markdown ONLY.
            - Each "news" item must be in a separate paragraph.
            - Put ONE blank line between items.
            - In each item, use asterisks for the bold "headline" of your fabricated news story.

            Create 5-7 of these "news stories" based on the provided material.

            Inspiration Material (Real News):
            {block}
        """).strip()

    def postprocess(self, llm_text: str) -> str:
        return (llm_text or "").strip()