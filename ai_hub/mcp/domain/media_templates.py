from __future__ import annotations
import re
from typing import List

def render_new_additions(lines: List[str], max_items: int = 8, title: str = "New arrivals") -> str:

    if not lines:
        return ""
    head = f"✨ {title} ({min(len(lines), max_items)}):"
    body = [f"• {x}" for x in lines[:max_items]]
    tail = [f"…and more {len(lines) - max_items}"] if len(lines) > max_items else []
    return "\n".join([head, *body, *tail])

def render_media_digest(new_lines: List[str], recommend_text: str | None) -> str:
    parts: List[str] = []

    new_block = render_new_additions(new_lines)
    if new_block:
        parts.append(new_block)

    rec = (recommend_text or "").strip()
    if rec:
        rec = re.sub(r"\n{3,}", "\n\n", rec)
        parts.append("🎯 Recommendations for you:\n" + rec)

    return "\n\n".join(parts).strip()
