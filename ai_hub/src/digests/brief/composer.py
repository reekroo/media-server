from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Optional
from ...core.router import Orchestrator
from .templates import BRIEF_FORMAT

class DailyBriefComposer:
    def __init__(self, orchestrator: Orchestrator):
        self._orchestrator = orchestrator

    async def compose(
        self,
        weather_json: Path,
        quakes_json: Optional[Path] = None,
        include_quakes: bool = True,
    ) -> str:
        weather_text = await self._get_weather_text(weather_json)
        
        quakes_text = ""
        if include_quakes:
            quakes_text = await self._get_quakes_text(quakes_json)

        brief = BRIEF_FORMAT.format(
            weather=weather_text,
            quakes=quakes_text,
        )
        return brief.strip()

    async def _get_weather_text(self, data_path: Path) -> str:
        payload = self._read_json_or_none(data_path)
        if not payload:
            return "Weather data is currently unavailable."
        
        return await self._orchestrator.run("weather.summary", payload)

    async def _get_quakes_text(self, data_path: Optional[Path]) -> str:
        payload = self._read_json_or_none(data_path)
        if not payload:
            return "" 
            
        return await self._orchestrator.run("quakes.assess", payload)

    @staticmethod
    def _read_json_or_none(path: Optional[Path]) -> dict[str, Any]:
        if not path or not path.exists():
            return {}
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            return {}