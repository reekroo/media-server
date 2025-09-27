from __future__ import annotations
from typing import List, Dict, Any, Optional

from functions.feeds.feed_collector import FeedItem

def format_items_for_prompt(items: List[Dict[str, Any]]) -> str:
    if not items:
        return "No items provided."
        
    feed_items = [FeedItem(**item) for item in items]
    item_lines = [f"- {item.title}: {item.summary}" for item in feed_items]
    return "\n".join(item_lines)

def create_summary_instruction(count: Optional[int], default: str = "Create 5-10 concise bullets") -> str:
    if isinstance(count, int) and count > 0:
        if count == 1:
            return "Focus on the single most important and recent event."
        else:
            return f"Create {count} concise bullets focusing on the most important events, what changed, and why it matters."
    else:
        return f"{default} focusing on the most important events, what changed, and why it matters."