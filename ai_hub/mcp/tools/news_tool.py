from __future__ import annotations
from typing import Any, Dict

from .base import ToolSpec
from mcp.rpc_methods.news import build_digest

_ALLOWED_DIGESTS = [
    "news", 
    "news_by", 
    "news_tr", 
    "news_eu", 
    "news_us", 
    "news_ru", 
    "news_ua",
    "news_fun",
    "gaming", 
    "entertainment",
]

_ALIASES = {
    "us": "news_us",
    "usa": "news_us",
    "america": "news_us",
    "eu": "news_eu",
    "europe": "news_eu",
    "ru": "news_ru",
    "russia": "news_ru",
    "by": "news_by",
    "belarus": "news_by",
    "ua": "news_ua",
    "ukraine": "news_ua",
    "tr": "news_tr",
    "turkey": "news_tr",
    "turkiye": "news_tr",
    "fun": "news_fun",
    "humor": "news_fun",
    "satire": "news_fun",
}

def _normalize_digest(value: str | None) -> str:
    raw = (value or "news").strip().lower()
    if raw in _ALLOWED_DIGESTS:
        return raw
    if raw in _ALIASES:
        return _ALIASES[raw]
    return "news"

async def _exec_news(app, args: Dict[str, Any]) -> str:
    digest = _normalize_digest(args.get("digest"))
    section = args.get("section")
    
    if not isinstance(section, str) or not section.strip():
        section = None

    count = args.get("count")
    if count and isinstance(count, (int, float)):
        count = int(count)
        if not (1 <= count <= 20):
            count = None
    else:
        count = None

    result_text = await build_digest(app, config_name=digest, section=section, count=count)
    return result_text or "No news items to show."

TOOL = ToolSpec(
    name="news_fetch",
    description=(
        "Fetch and summarize recent news. Choose a named digest (e.g., 'news', 'news_tr'). "
        "Optionally narrow to a section. You can also specify the exact number of news items to return."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "digest": {
                "type": "string",
                "description": (
                    "Which configured news digest to use: one of "
                    + ", ".join(_ALLOWED_DIGESTS)
                )
            },
            "section": {
                "type": "string",
                "description": "Optional section/category to summarize only that part"
            },
            "count": {
                "type": "integer",
                "description": "Optional. The exact number of news items to summarize (e.g., 1 for the latest, 3 for the top 3)."
            }
        },
        "additionalProperties": False,
    },
    execute=_exec_news,
)