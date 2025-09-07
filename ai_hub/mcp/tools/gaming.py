from __future__ import annotations
from src.app import App

async def gaming_digest(app: App, config: str = "configs/gaming.toml") -> str:
    return await app.services.dispatcher.run("gaming", app=app, config=config)
