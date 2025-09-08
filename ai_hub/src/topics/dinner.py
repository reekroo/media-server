from __future__ import annotations
from .base import TopicHandler
import textwrap

class DinnerRecipeTopic(TopicHandler):
    def build_prompt(self, payload: dict) -> str:
        prefs = payload.get("preferences", {})

        return textwrap.dedent(f"""
            You are a helpful and creative home cook assistant for a family of 2 adults and 1 child.
            Your task is to answer the eternal question: "What's for dinner?".

            Suggest 3-4 simple, easy-to-prepare recipes for tonight's dinner.
            The meals should be healthy, delicious, and not require advanced skills or a lot of cleanup.

            IMPORTANT: Format your response using simple Markdown. Use asterisks for bold (*bold text*).

            Strictly follow these preferences:
            - Cuisine style: {prefs.get("cuisine", "any")}
            - Exclude these ingredients: {prefs.get("exclude_ingredients", "none")}
            - Maximum preparation time: {prefs.get("max_prep_time_minutes", 30)} minutes
            - Maximum total cooking time: {prefs.get("max_cook_time_minutes", 60)} minutes
            - Other notes: {prefs.get("other", "none")}

            For each recipe, provide:
            1. A catchy name for the dish in bold (e.g., *Speedy Chicken Stir-Fry*).
            2. A one-sentence description explaining why it's a good choice.
            3. A bulleted list of the main ingredients.

            Do not provide full cooking instructions, only the ideas and main components.
        """).strip()

    def postprocess(self, llm_text: str) -> str:
        return (llm_text or "").strip()