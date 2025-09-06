from __future__ import annotations
from pathlib import Path
import json
from typing import Optional
from ...core.router import Orchestrator
from .templates import BRIEF_FORMAT

def _read_json_or_none(p: Optional[Path]) -> dict:
    if not p or not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))

async def build_daily_brief(
    orch: Orchestrator,
    weather_json: Path,
    quakes_json: Optional[Path] = None,
    include_quakes: bool = True,
) -> str:
    weather_payload = _read_json_or_none(weather_json)
    weather_text = await orch.run("weather.summary", weather_payload)

    quakes_block = ""
    if include_quakes and quakes_json:
        quakes_payload = _read_json_or_none(quakes_json)
        if quakes_payload:
            quakes_text = await orch.run("quakes.assess", quakes_payload)
            quakes_block = f"🌍 Seismic\n{quakes_text}\n\n"

    brief = BRIEF_FORMAT.format(
        weather=weather_text.strip(),
        quakes_block=quakes_block,
    )
    return brief.strip()
