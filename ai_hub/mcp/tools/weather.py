from __future__ import annotations
from src.app import App

async def weather_summary(app: App, payload: dict | None = None) -> str:
    return await app.services.dispatcher.run("weather", app=app, payload=payload or {})
