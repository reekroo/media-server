from __future__ import annotations
import tomllib
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..app import App

from ..digests.dinner.templates import render_dinner_digest

async def run(app: App, config_path_override: str | None = None) -> list[str]:
    svc = app.services
    config_path = Path(config_path_override) if config_path_override else svc.settings.BASE_DIR / "configs" / "dinner.toml"
    if not config_path.exists():
        return ["Dinner ideas config not found."]

    cfg = tomllib.loads(config_path.read_text("utf-8"))
    if not cfg.get("enabled", False):
        return []

    payload = {"preferences": cfg.get("preferences", {})}
    summary = await svc.orchestrator.run("dinner.suggest", payload)
    return [render_dinner_digest(summary)]
