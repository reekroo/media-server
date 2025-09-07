from __future__ import annotations
from src.app import App

async def turkish_news_digest(app: App, config: str = "configs/news_tr.toml") -> str:
    return await app.services.dispatcher.run("turkish_news", app=app, config=config)
