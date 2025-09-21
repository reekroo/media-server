import textwrap
from .base import TopicHandler
from .utils import format_items_for_prompt

class EntertainmentDigestTopic(TopicHandler):
    def build_prompt(self, payload: dict) -> str:
        items = payload.get("items", [])
        count = payload.get("count")

        block = format_items_for_prompt(items)

        if isinstance(count, int) and count > 0:
            focus_instruction = f"Focus on the top {count} most important items (releases, trailers, casting news)."
        else:
            focus_instruction = "Focus on:\n1. Major new releases...\n2. Significant trailers...\n3. Interesting casting news."

        return textwrap.dedent(f"""
            You are a film and TV critic for a modern magazine.
            From the news items below, create a concise and engaging digest about what's new and upcoming.

            IMPORTANT, OUTPUT FORMAT (STRICT):
            - Use simple Markdown ONLY.
            - Section titles with asterisks: *Movies*, *TV/Series*.
            - Put ONE blank line between items.
                               
            {focus_instruction}

            Structure your output into two short sections: *Movies* and *TV/Series*.

            News Items:
                {block}
        """).strip()