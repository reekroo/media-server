import textwrap
from .base import TopicHandler
from .utils import format_items_for_prompt, create_summary_instruction

class UkraineNewsDigestTopic(TopicHandler):
    def build_prompt(self, payload: dict) -> str:
        items = payload.get("items", [])
        section = payload.get("section", "news")
        count = payload.get("count")

        block = format_items_for_prompt(items)
        # Для украинского языка можно передать дефолтную инструкцию на украинском
        summary_instruction = create_summary_instruction(count, default="Створіть 5-10 коротких пунктів")

        return textwrap.dedent(f"""
            You are a news editor summarizing news from Ukraine.
            Analyze the following news items from Ukrainian sources on the topic of '{section}'.
            Your final summary MUST be in Ukrainian.

            IMPORTANT, OUTPUT FORMAT (STRICT):
            - Use simple Markdown ONLY.
            - Use asterisks for bold section titles (*Назва розділу*).
            - Put ONE blank line between items.

            {summary_instruction}

            News Items (from Ukraine):
                {block}
        """).strip()