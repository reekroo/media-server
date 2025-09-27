import textwrap
from typing import Any, Dict, List

from .base import TopicHandler
from .formatters.base import Formatter
from .formatters.markdown_dinner_formatter import DinnerFormatter

MIN_COUNT = 1
MAX_COUNT = 5
DEFAULT_COUNT = 3

PROMPT_TMPL = """\
You are a home–cooking assistant.
Return exactly **{n}** diverse dinner ideas as a compact digest.

OUTPUT CONTRACT:
- Produce exactly {n} ideas, each separated by a single blank line.
- Start each idea with a header line: "🍽️ *Idea X: Dish name*" where X is 1..{n}.
- Do not add intro/outro text.

FORMAT (Telegram MarkdownV2-safe):
- Use ONLY *bold* for section titles, _italic_ for a one-line hook.
- Use "- " bullets for ingredients; "1." numbers for steps.
- No links, code blocks, tables, or block quotes.
- Avoid characters requiring escapes: []()~`>#+=|{{}}!.
- Keep lines ≤ 120 chars.

SECTION LAYOUT for each idea:
🍽️ *Idea X: Dish name*
_One enticing line, ≤ 100 chars._
🥗 *Ingredients*
- 3 to 5 short bullets
👩‍🍳 *Steps*
1. Concise action.
2. Concise action.
3. Concise action.
📊 *Nutrition* ~X kcal  Protein Y g  Fat Z g  Carbs W g
(Include Nutrition only if reasonably inferable; otherwise omit the line.)

GUIDELINES:
- Respect user preferences where possible; otherwise pick accessible options.
- Practical, easy-to-cook, kid-friendly if asked. No long paragraphs.

User Preferences:
{prefs_block}
"""

def _clamp_count(raw: Any) -> int:
    try:
        n = int(raw) if raw is not None else DEFAULT_COUNT
    except Exception:
        n = DEFAULT_COUNT
    if n < MIN_COUNT: n = MIN_COUNT
    if n > MAX_COUNT: n = MAX_COUNT
    return n

def _prefs_block(prefs: Dict[str, Any]) -> str:
    lines: List[str] = []
    if prefs.get("cuisine"):
        lines.append(f"- Cuisine: {prefs['cuisine']}")
    if prefs.get("exclude_ingredients"):
        lines.append(f"- Exclude ingredients: {prefs['exclude_ingredients']}")
    if prefs.get("max_prep_time_minutes"):
        lines.append(f"- Max prep time: {prefs['max_prep_time_minutes']} minutes")
    if prefs.get("max_cook_time_minutes"):
        lines.append(f"- Max cook time: {prefs['max_cook_time_minutes']} minutes")
    if prefs.get("other"):
        lines.append(f"- Notes: {prefs['other']}")
    return "\n".join(lines) if lines else "- (none)"


class DinnerTopic(TopicHandler):
    @property
    def formatter(self) -> Formatter:
        return DinnerFormatter()

    @property
    def empty_response_text(self) -> str:
        return ""

    def build_prompt(self, payload: dict) -> str:
        prefs = payload.get("preferences", {}) or {}
        n = _clamp_count(payload.get("count"))
        return textwrap.dedent(PROMPT_TMPL.format(
            n=n,
            prefs_block=_prefs_block(prefs),
        )).strip()