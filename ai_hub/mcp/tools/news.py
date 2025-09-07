from __future__ import annotations
from src.app import App

async def news_digest(app: App, config: str = "configs/news.toml", section: str | None = None) -> str:
    return await app.services.dispatcher.run("news", app=app, config=config, section=section)
