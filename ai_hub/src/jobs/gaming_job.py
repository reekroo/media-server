from __future__ import annotations
import tomllib
from pathlib import Path
from dataclasses import asdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..app import App

from ..digests.gaming.templates import render_gaming_digest

async def run(app: App, config_path_override: str | None = None) -> list[str]:
    svc = app.services
    config_path = Path(config_path_override) if config_path_override else svc.settings.BASE_DIR / "configs" / "gaming.toml"
    if not config_path.exists():
        return []

    cfg = tomllib.loads(config_path.read_text("utf-8"))
    if not cfg.get("enabled", False):
        return []

    all_urls = [url for urls in cfg.get("feeds", {}).values() for url in urls]
    if not all_urls:
        return []

    all_items = await svc.feed_collector.collect(all_urls)
    if not all_items:
        return []

    items_payload = [asdict(item) for item in all_items[:int(cfg.get("max_items", 20))]]
    summary = await svc.orchestrator.run("gaming.digest", {"items": items_payload})
    return [render_gaming_digest(summary)]
