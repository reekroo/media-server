from __future__ import annotations
from src.app import App

async def analytics_digest(app: App) -> str:
    return await app.run_log_digest()