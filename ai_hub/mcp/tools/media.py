from __future__ import annotations
from src.app import App

async def media_digest(app: App, config: str = "configs/media.toml") -> str:
    return await app.services.dispatcher.run("media", app=app, config=config)
