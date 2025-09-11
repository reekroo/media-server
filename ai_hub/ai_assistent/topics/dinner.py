from .base import TopicHandler
import textwrap

class DinnerTopic(TopicHandler): # Убедись, что класс наследуется от TopicHandler
    def build_prompt(self, payload: dict) -> str:
        prefs = payload.get("preferences", {})
        
        # Формируем текстовое описание предпочтений для промпта
        prefs_lines = []
        if cuisine := prefs.get("cuisine"):
            prefs_lines.append(f"- Cuisine: {cuisine}")
        if exclude := prefs.get("exclude_ingredients"):
            prefs_lines.append(f"- Exclude ingredients: {exclude}")
        if prep_time := prefs.get("max_prep_time_minutes"):
            prefs_lines.append(f"- Max prep time: {prep_time} minutes")
        if cook_time := prefs.get("max_cook_time_minutes"):
            prefs_lines.append(f"- Max cook time: {cook_time} minutes")
        if other := prefs.get("other"):
            prefs_lines.append(f"- Other notes: {other}")
            
        prefs_block = "\n".join(prefs_lines)

        return textwrap.dedent(f"""
            You are a creative home cook assistant. Suggest 3 diverse and interesting dinner ideas for tonight.
            
            IMPORTANT: Format your response using simple Markdown. Use asterisks for bold titles (*Idea 1: ...*).
            
            User Preferences:
            {prefs_block}

            For each idea, provide:
            1. A catchy name.
            2. A brief, enticing description (2-3 sentences).
            3. A simple list of main ingredients.
        """).strip()

    def postprocess(self, llm_text: str) -> str:
        return (llm_text or "").strip()