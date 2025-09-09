from __future__ import annotations
from src.app import App

async def dinner_ideas(app: App, config: str = "configs/dinner.toml") -> str:
    return await app.services.dispatcher.run("dinner", app=app, config=config)
