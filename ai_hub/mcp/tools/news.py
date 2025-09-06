from __future__ import annotations
import asyncio, tomllib
from pathlib import Path
from src.core.settings import Settings
from src.core.agents.factory import agent_factory
from src.core.router import Orchestrator
from src.topics.news import NewsDigestTopic
from src.digests.news.collector import collect_feeds
from src.digests.news.templates import render_news_digest

def _orch() -> Orchestrator:
    s = Settings()
    agent = agent_factory(api_key=s.GEMINI_API_KEY)
    topics = {"news.digest": NewsDigestTopic()}
    return Orchestrator(agent, topics)

def news_digest(config: str = "configs/news.toml", section: str | None = None) -> str:
    cfgp = Path(config)
    if not cfgp.exists():
        return "news: config not found"
    
    cfg = tomllib.loads(cfgp.read_text("utf-8"))
    feeds = cfg.get("feeds", {})
    max_items = int(cfg.get("max_items", 20))

    if not feeds:
        return "news: no feeds configured"

    key = section if section in feeds else (next(iter(feeds.keys())) if feeds else None)
    if not key:
        return "news: no section available"

    items = collect_feeds(list(feeds[key]), max_items=max_items)
    if not items:
        return f"news: no items for section '{key}'"

    orch = _orch()
    payload = {"items": items, "section": key}

    async def _run():
        return await orch.run("news.digest", payload)
    
    summary = asyncio.run(_run())
    return render_news_digest(key, summary)
