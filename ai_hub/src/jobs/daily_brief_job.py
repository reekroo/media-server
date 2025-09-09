from __future__ import annotations
import tomllib
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..app import App

from ..digests.brief.composer import DailyBriefComposer

async def run(app: App, config_path_override: str | None = None) -> list[str]:
    svc = app.services
    config_path = Path(config_path_override) if config_path_override else svc.settings.BASE_DIR / "configs" / "daily.toml"
    if not config_path.exists():
        return ["Daily brief config not found."]

    cfg_data = tomllib.loads(config_path.read_text("utf-8")).get("brief", {})

    composer = DailyBriefComposer(svc.orchestrator)

    weather_path = Path(svc.settings.daily.weather_json)
    quakes_path = Path(svc.settings.daily.quakes_json)

    brief = await composer.compose(
        weather_json=weather_path,
        quakes_json=quakes_path,
        include_quakes=cfg_data.get("include_quakes", True),
    )
    return [brief]
