from __future__ import annotations
import re
import textwrap
from typing import Any, Dict, List

from .base import TopicHandler

MIN_COUNT = 1
MAX_COUNT = 5
DEFAULT_COUNT = 3

HEADER_RE = re.compile(r'^🍽️ \*Idea\s+(\d+):\s.*?\*$', re.MULTILINE)

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
📊 *Nutrition*  ~X kcal  Protein Y g  Fat Z g  Carbs W g
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

def _normalize_markdown(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text.strip())
    text = re.sub(r"^[•●]\s*", "- ", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*(\d+)\)\s", r"\1. ", text, flags=re.MULTILINE)
    text = "\n".join(ln.rstrip() for ln in text.splitlines())
    def fix_marks(ln: str) -> str:
        if ln.count("*") % 2: ln = ln.replace("*", "")
        if ln.count("_") % 2: ln = ln.replace("_", "")
        return ln
    return "\n".join(fix_marks(ln) for ln in text.splitlines()).strip()

def _slice_exact_n_ideas(text: str, n: int) -> str:
    matches = list(HEADER_RE.finditer(text))
    if not matches:
        return text
    if len(matches) > n:
        cut_at = matches[n].start()
        text = text[:cut_at].rstrip()
    return text

class DinnerTopic(TopicHandler):
    def build_prompt(self, payload: dict) -> str:
        prefs = payload.get("preferences", {}) or {}
        n = _clamp_count(payload.get("count"))
        return textwrap.dedent(PROMPT_TMPL.format(
            n=n,
            prefs_block=_prefs_block(prefs),
        )).strip()

    def postprocess(self, llm_text: str) -> str:
        if not llm_text:
            return ""
        cleaned = _normalize_markdown(llm_text)
        numbers = [int(m.group(1)) for m in HEADER_RE.finditer(cleaned)]
        desired_n = max(numbers) if numbers else DEFAULT_COUNT
        desired_n = max(MIN_COUNT, min(MAX_COUNT, desired_n))
        return _slice_exact_n_ideas(cleaned, desired_n)
