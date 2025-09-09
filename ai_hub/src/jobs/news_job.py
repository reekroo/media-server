from __future__ import annotations
import tomllib
from pathlib import Path
from dataclasses import asdict
from typing import TYPE_CHECKING

if TYPE_CHECKING: 
    from ..app import App

from ..digests.news.templates import render_news_digest

async def run(app: App, config_path_override: str | None = None, section: str | None = None) -> list[str]:
    svc = app.services
    config_path = Path(config_path_override) if config_path_override else svc.settings.BASE_DIR / "configs" / "news.toml"
    if not config_path.exists():
        return []

    cfg = tomllib.loads(config_path.read_text("utf-8"))
    if not cfg.get("enabled", False):
        return []

    feeds = cfg.get("feeds", {})
    messages = []
    for sec_name, urls in feeds.items():
        if section and section != sec_name:
            continue

        items = await svc.feed_collector.collect(urls, max_items=int(cfg.get("max_items", 20)))
        if not items:
            continue

        items_payload = [asdict(item) for item in items]
        summary = await svc.orchestrator.run("news.digest", {"items": items_payload, "section": sec_name})
        messages.append(render_news_digest(sec_name, summary))

    return messages
