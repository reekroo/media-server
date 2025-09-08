from __future__ import annotations
import tomllib
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING: from ..app import App
from ..digests.sys.build import SystemDigestBuilder

async def run(app: App, config_path_override: str | None = None) -> list[str]:
    svc = app.services
    config_path = Path(config_path_override) if config_path_override else svc.settings.BASE_DIR / "configs" / "sys.toml"
    if not config_path.exists():
        return ["System digest config not found."]

    cfg = tomllib.loads(config_path.read_text("utf-8"))
    if not cfg.get("enabled", True):
        return []

    builder = SystemDigestBuilder(
        config=cfg,
        incidents_dir=svc.settings.STATE_DIR / "incidents",
        state_path=svc.settings.STATE_DIR / "sys_digest.json",
    )

    _, msg = await builder.build()
    return [msg]
