from __future__ import annotations
from typing import Any, Dict, List, Union

from .base import ToolSpec
from mcp.rpc_methods.news import build_digest

_ALLOWED_DIGESTS = [
    "news", 
    "news_by", 
    "news_tr", 
    "news_eu", 
    "news_us", 
    "news_ru", 
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

def _ensure_text(result: Union[str, List[str]]) -> str:
    if isinstance(result, list):
        text = "\n\n---\n\n".join([s for s in result if s and s.strip()])
        return text or "No news items to show."
    return result or "No news items to show."

async def _exec_news(app, args: Dict[str, Any]) -> str:
    digest = _normalize_digest(args.get("digest"))
    section = args.get("section")
    if not isinstance(section, str) or not section.strip():
        section = None

    result = await build_digest(app, config_name=digest, section=section)
    return _ensure_text(result)

TOOL = ToolSpec(
    name="news_fetch",
    description=(
        "Fetch and summarize recent news. Choose a named digest (e.g., 'news', 'news_tr', "
        "'news_us', 'gaming', 'entertainment'). Optionally narrow to a section "
        "(like 'tech', 'world', 'economy') if applicable."
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
            }
        },
        "additionalProperties": False,
    },
    execute=_exec_news,
)
