from __future__ import annotations
import asyncio, tomllib
from pathlib import Path
from src.core.settings import Settings
from src.core.agents.factory import agent_factory
from src.core.router import Orchestrator
from src.topics.gaming import GamingDigestTopic
from src.digests.gaming.collector import collect_feeds
from src.digests.gaming.templates import render_gaming_digest

def _orch() -> Orchestrator:
    s = Settings()
    agent = agent_factory(api_key=s.GEMINI_API_KEY)
    topics = {"gaming.digest": GamingDigestTopic()}
    return Orchestrator(agent, topics)

def gaming_digest(config: str = "configs/gaming.toml") -> str:
    """
    MCP tool: gaming.digest
    params:
      - config: путь к TOML конфигу игровых фидов.
    returns: str — краткая сводка по игровому миру.
    """
    cfgp = Path(config)
    if not cfgp.exists():
        return "gaming: config not found"
    cfg = tomllib.loads(cfgp.read_text("utf-8"))
    feeds = cfg.get("feeds", {})
    max_items = int(cfg.get("max_items", 20))
    if not feeds:
        return "gaming: no feeds configured"

    # собрать все разделы вместе (gaming.*)
    items = []
    for _, urls in feeds.items():
        items.extend(collect_feeds(list(urls), max_items=max_items))
    if not items:
        return "gaming: no items"

    orch = _orch()
    payload = {"items": items[:max_items]}

    async def _run():
        return await orch.run("gaming.digest", payload)
    summary = asyncio.run(_run())
    return render_gaming_digest(summary)
