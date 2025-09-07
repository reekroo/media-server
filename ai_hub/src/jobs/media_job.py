# media_job.py
from __future__ import annotations
import tomllib
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING: from ..app import App

from ..digests.media.collector import NewTitlesCollector
from ..digests.media.recommender import MediaRecommender
from ..digests.media.templates import render_media_digest

async def run(app: App, config_path_override: str | None = None) -> list[str]:
    svc = app.services
    config_path = Path(config_path_override) if config_path_override else svc.settings.BASE_DIR / "configs" / "media.toml"
    if not config_path.exists():
        return ["Media config not found."]

    cfg = tomllib.loads(config_path.read_text("utf-8"))
    if not cfg.get("enabled", True):
        return []

    state_path = svc.settings.BASE_DIR / Path(cfg.get("state_path", "state/media_index.json"))
    root_path = Path(cfg.get("root", "/media"))

    collector = NewTitlesCollector(state_path=state_path, include_ext=cfg.get("include_ext", []), max_depth=int(cfg.get("max_depth", 6)))
    new_titles = await collector.collect(root=root_path)

    recommender = MediaRecommender(svc.orchestrator)
    rec_text = await recommender.build(root=root_path, prefs=cfg.get("recommender", {}), cap=int(cfg.get("cap", 600)))

    return [render_media_digest(new_titles=new_titles, recommend_text=rec_text)]
