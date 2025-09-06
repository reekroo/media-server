from __future__ import annotations
from src.app import App

async def turkish_news_digest(app: App) -> list[str]:
    return await app.run_turkish_news_digest()