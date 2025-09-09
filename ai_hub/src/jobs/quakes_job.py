from __future__ import annotations
import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..app import App

async def run(app: App, payload: dict | None = None) -> list[str]:
    svc = app.services
    if not payload:
        quakes_path = Path(svc.settings.daily.quakes_json)
        if not quakes_path.exists():
            return ["Quakes data file not found."]
        payload = json.loads(quakes_path.read_text("utf-8"))

    summary = await svc.orchestrator.run("quakes.summary", payload or {})
    return [summary]
