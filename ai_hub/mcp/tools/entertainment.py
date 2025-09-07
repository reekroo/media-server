from __future__ import annotations
from src.app import App

async def entertainment_digest(app: App, config: str = "configs/entertainment.toml") -> str:
    return await app.services.dispatcher.run("entertainment", app=app, config=config)
