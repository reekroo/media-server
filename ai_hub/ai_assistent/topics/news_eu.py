import textwrap
from .base import TopicHandler
from .utils import format_items_for_prompt, create_summary_instruction

class EuropeanNewsDigestTopic(TopicHandler):
    def build_prompt(self, payload: dict) -> str:
        items = payload.get("items", [])
        section = payload.get("section", "news")
        count = payload.get("count")

        block = format_items_for_prompt(items)
        summary_instruction = create_summary_instruction(count)

        return textwrap.dedent(f"""
            You are a news editor summarizing European Union news for an international audience.
            Analyze the following news items from European sources on the topic of '{section}'.
            Your final summary MUST be in English.

            IMPORTANT, OUTPUT FORMAT (STRICT):
            - Use simple Markdown ONLY.
            - Use asterisks for bold section titles (*Title*).
            - Put ONE blank line between items.

            {summary_instruction}

            News Items (from Europe):
                {block}
        """).strip()