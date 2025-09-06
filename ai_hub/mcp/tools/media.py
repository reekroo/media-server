from __future__ import annotations
from src.app import App

async def media_digest(app: App, config: str = "configs/media.toml") -> str:
    return await app.run_media_digest(config_path_override=config)