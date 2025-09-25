from __future__ import annotations
from typing import Any, Dict, List

from .base import ToolSpec
from mcp.rpc_methods.news.rpc import build_digest
from core.constants.news import UNIVERSAL_NEWS_DIGESTS, DIGEST_ALIASES

def _normalize_digest(value: str | None) -> str:
    raw = (value or "news").strip().lower()
    if raw in UNIVERSAL_NEWS_DIGESTS:
        return raw
    if raw in DIGEST_ALIASES:
        return DIGEST_ALIASES[raw]
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

    results_list: List[str] = await build_digest(app, config_name=digest, section=section, count=count)

    if not results_list:
        return "No news items to show."

    final_text = "\n\n---\n\n".join(results_list)
    return final_text

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
                    + ", ".join(UNIVERSAL_NEWS_DIGESTS)
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