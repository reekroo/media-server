from __future__ import annotations
from typing import List, Dict

def format_items_for_prompt(items: List[Dict]) -> str:
    lines = []
    for item in items:
        title = item.get("title", "")
        summary = item.get("summary", "")
        lines.append(f"- {title} — {summary}")
    return "\n".join(lines)