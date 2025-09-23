from __future__ import annotations
import re
import textwrap
from .base import TopicHandler

class DinnerTopic(TopicHandler):
    def build_prompt(self, payload: dict) -> str:
        prefs = payload.get("preferences", {}) or {}

        prefs_lines = []
        if prefs.get("cuisine"):
            prefs_lines.append(f"- Cuisine: {prefs['cuisine']}")
        if prefs.get("exclude_ingredients"):
            prefs_lines.append(f"- Exclude ingredients: {prefs['exclude_ingredients']}")
        if prefs.get("max_prep_time_minutes"):
            prefs_lines.append(f"- Max prep time: {prefs['max_prep_time_minutes']} minutes")
        if prefs.get("max_cook_time_minutes"):
            prefs_lines.append(f"- Max cook time: {prefs['max_cook_time_minutes']} minutes")
        if prefs.get("other"):
            prefs_lines.append(f"- Notes: {prefs['other']}")
        prefs_block = "\n".join(prefs_lines) if prefs_lines else "- (none)"

        return textwrap.dedent(f"""
            You are a home–cooking assistant.
            Return exactly **3** diverse dinner ideas for tonight as a compact digest.

            FORMAT & MARKDOWN (Telegram MarkdownV2):
            - Use ONLY these Markdown features:
              *bold* for titles, _italic_ for the one–line hook.
              Hyphen bullets ("- ") for ingredients.
              Numbered list ("1.", "2.", "3.") for steps.
            - Do NOT use links, code blocks, tables, quotes, or backticks.
            - Avoid characters that require escaping: [ ] ( ) ~ ` > # + = | {{ }} ! .
              Also avoid underscores in plain text except for _italic_ markers.
              Use commas instead of parentheses.
            - Keep each line <= 120 chars.

            LAYOUT (for each idea; repeat 3 times):
            🍽️ *Idea N: Dish name*
            _One enticing line, <= 100 chars._
            🥗 *Ingredients*
            - 3 to 5 short ingredient bullets
            👩‍🍳 *Steps*
            1. Concise action, one sentence.
            2. Concise action, one sentence.
            3. Concise action, one sentence.
            📊 *Nutrition*  ~X kcal  Protein Y g  Fat Z g  Carbs W g
            (Include Nutrition only if reasonably inferable. Otherwise omit the whole line.)

            GLOBAL RULES:
            - Practical, easy–to–cook ideas.
            - No long paragraphs; keep it scan–friendly.
            - Respect user preferences if possible, else choose accessible options.

            User Preferences:
            {prefs_block}
        """).strip()

    def postprocess(self, llm_text: str) -> str:
        text = (llm_text or "").strip()
        if not text:
            return text

        text = re.sub(r"\n{3,}", "\n\n", text)

        text = re.sub(r"^[•\u2022]\s*", "- ", text, flags=re.MULTILINE)     # dot bullets -> hyphen
        text = re.sub(r"^\s*-\s{2,}", "- ", text, flags=re.MULTILINE)       # "-   " -> "- "
        text = re.sub(r"^\s*(\d+)\)\s", r"\1. ", text, flags=re.MULTILINE)  # "1) " -> "1. "

        def _fix_line_marks(ln: str) -> str:
            stars = ln.count("*")
            underscores = ln.count("_")
            if stars % 2 != 0:
                ln = ln.replace("*", "")
            if underscores % 2 != 0:
                ln = ln.replace("_", "")
            return ln

        lines = [_fix_line_marks(ln.rstrip()) for ln in text.splitlines()]
        cleaned = "\n".join(lines).strip()

        return cleaned
