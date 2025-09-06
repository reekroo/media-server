from __future__ import annotations
from src.app import App

async def entertainment_digest(app: App) -> str:
    return await app.run_entertainment_digest()