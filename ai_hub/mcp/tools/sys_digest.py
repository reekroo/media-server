from __future__ import annotations
from src.app import App

async def system_digest(app: App, config: str = "configs/sys.toml") -> str:
    return await app.services.dispatcher.run("sys", app=app, config=config)
