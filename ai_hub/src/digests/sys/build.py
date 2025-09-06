from __future__ import annotations
from pathlib import Path
import json
from typing import Dict, List, Any
import tomllib
import aiofiles
from .collector import get_unit_status, get_unit_logs
from .rules import classify
from .model import DigestSummary, UnitReport, Incident
from .templates import render_digest

class SystemDigestBuilder:
    def __init__(self, config: Dict[str, Any], incidents_dir: Path, state_path: Path):
        self.config = config
        self.incidents_dir = incidents_dir
        self.state_path = state_path        
        self.lookback = self.config.get("lookback", "24h")
        self.min_prio = self.config.get("min_priority", "warning")
        self.max_restarts = int(self.config.get("max_restarts", 3))
        self.units: List[str] = list(self.config.get("units", []))
        self.patterns: Dict[str, List[str]] = dict(self.config.get("patterns", {}))

    async def build(self) -> tuple[DigestSummary, str]:
        reports: List[UnitReport] = []
        for unit_name in self.units:
            status = await get_unit_status(unit_name)
            logs = await get_unit_logs(unit_name, lookback=self.lookback, min_priority=self.min_prio)
            report = classify(status, logs, self.patterns, self.max_restarts)
            reports.append(report)
            
            if report.level in ("WARN", "FAIL"):
                incident = self._create_incident_from_report(report)
                await self._save_incident(incident)

        overall = self._determine_overall_level(reports)

        digest = DigestSummary(
            lookback=self.lookback,
            min_priority=self.min_prio,
            overall=overall,
            reports=reports
        )
        
        await self._save_state(digest)
        
        text_report = render_digest(digest)
        return digest, text_report

    def _create_incident_from_report(self, report: UnitReport) -> Incident:
        return Incident(
            id=self._stable_id(report.unit, report.level, report.status.restarts),
            unit=report.unit,
            level=report.level,
            reason=report.issues,
            restarts=report.status.restarts,
            active=report.status.active,
            samples=report.samples,
        )

    async def _save_incident(self, incident: Incident) -> None:
        self.incidents_dir.mkdir(parents=True, exist_ok=True)
        file_path = self.incidents_dir / f"{incident.id}.json"
        async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(incident.model_dump(), ensure_ascii=False, indent=2))

    async def _save_state(self, digest: DigestSummary) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(self.state_path, "w", encoding="utf-8") as f:
            await f.write(json.dumps(digest.model_dump(), ensure_ascii=False, indent=2))

    @staticmethod
    def _determine_overall_level(reports: List[UnitReport]) -> str:
        if any(r.level == "FAIL" for r in reports):
            return "FAIL"
        if any(r.level == "WARN" for r in reports):
            return "WARN"
        return "OK"

    @staticmethod
    def _stable_id(unit: str, level: str, restarts: int) -> str:
        return f"{unit.replace('.', '_')}__{level}__r{restarts}"

async def build_system_digest(*, config_path: Path, incidents_dir: Path, state_path: Path) -> tuple[DigestSummary, str]:
    try:
        config = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        config = {}
        
    builder = SystemDigestBuilder(config, incidents_dir, state_path)
    return await builder.build()