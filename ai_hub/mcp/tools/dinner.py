from __future__ import annotations
from src.app import App

async def dinner_ideas(app: App) -> str:
    return await app.run_dinner_digest()