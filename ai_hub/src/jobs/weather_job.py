# weather_job.py
from __future__ import annotations
import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..app import App

async def run(app: App, payload: dict | None = None) -> list[str]:
    svc = app.services
    if not payload:
        weather_path = Path(svc.settings.daily.weather_json)
        if not weather_path.exists():
            return ["Weather data file not found."]
        payload = json.loads(weather_path.read_text("utf-8"))

    summary = await svc.orchestrator.run("weather.summary", payload or {})
    return [summary]
