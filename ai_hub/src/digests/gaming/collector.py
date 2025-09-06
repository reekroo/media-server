from __future__ import annotations
from typing import List, Dict, Any
import feedparser

def collect_feeds(feeds: list[str], *, max_items: int = 20) -> list[dict]:
    items: list[dict] = []
    for url in feeds:
        try:
            d = feedparser.parse(url)
            for e in (d.entries or [])[:max_items]:
                items.append({
                    "title": getattr(e, "title", ""),
                    "summary": getattr(e, "summary", "") or getattr(e, "subtitle", ""),
                    "link": getattr(e, "link", ""),
                })
        except Exception:
            continue
    return items[:max_items]
