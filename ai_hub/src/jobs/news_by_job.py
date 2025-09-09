from __future__ import annotations
import tomllib
from pathlib import Path
from dataclasses import asdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..app import App

from ..digests.news_by.templates import render_belarus_news_digest

async def run(app: App, config_path_override: str | None = None) -> list[str]:
    svc = app.services
    config_path = Path(config_path_override) if config_path_override else svc.settings.BASE_DIR / "configs" / "news_by.toml"
    if not config_path.exists():
        return []

    cfg = tomllib.loads(config_path.read_text("utf-8"))
    if not cfg.get("enabled", False):
        return []

    feeds = cfg.get("feeds", {})
    messages = []
    for section, urls in feeds.items():
        items = await svc.feed_collector.collect(urls, max_items=int(cfg.get("max_items", 25)))
        if not items:
            continue

        items_payload = [asdict(item) for item in items]
        summary = await svc.orchestrator.run("news.by.digest", {"items": items_payload, "section": section})
        messages.append(render_belarus_news_digest(section, summary))
    return messages
