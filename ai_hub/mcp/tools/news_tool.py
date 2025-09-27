from __future__ import annotations
from typing import Any, Dict, List

from .base import ToolSpec
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
    count = args.get("count")

    params = {"config_name": digest}
    if section:
        params["section"] = section
    if count and isinstance(count, (int, float)) and 1 <= int(count) <= 20:
        params["count"] = int(count)

    results_list: List[str] = await app.dispatcher.run("news.build", **params)

    if not results_list:
        return "No news items to show."

    return "\n\n".join(results_list)

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