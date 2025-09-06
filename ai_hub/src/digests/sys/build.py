from __future__ import annotations
from pathlib import Path
import json
from typing import Dict, List
from .collector import get_unit_status, get_unit_logs
from .rules import classify
from .model import DigestSummary, UnitReport, Incident
from .templates import render_digest

def _read_toml(path: Path) -> dict:
    import tomllib
    return tomllib.loads(path.read_text(encoding="utf-8"))

def _save_incident(inc: Incident, root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / f"{inc.id}.json").write_text(json.dumps(inc.model_dump(), ensure_ascii=False, indent=2))

def _stable_id(unit: str, level: str, restarts: int) -> str:
    return f"{unit.replace('.','_')}__{level}__r{restarts}"

def build_system_digest(*, config_path: Path, incidents_dir: Path, state_path: Path) -> tuple[DigestSummary, str]:
    cfg = _read_toml(config_path)
    lookback = cfg.get("lookback", "24h")
    min_prio = cfg.get("min_priority", "warning")
    max_restarts = int(cfg.get("max_restarts", 3))
    units: List[str] = list(cfg.get("units", []))
    patterns: Dict[str, List[str]] = dict(cfg.get("patterns", {}))

    reports: List[UnitReport] = []
    for u in units:
        status = get_unit_status(u)
        logs = get_unit_logs(u, lookback=lookback, min_priority=min_prio)
        rep = classify(status, logs, patterns, max_restarts)
        reports.append(rep)
        if rep.level in ("WARN", "FAIL"):
            inc = Incident(
                id=_stable_id(rep.unit, rep.level, rep.status.restarts),
                unit=rep.unit,
                level=rep.level,
                reason=rep.issues,
                restarts=rep.status.restarts,
                active=rep.status.active,
                samples=rep.samples,
            )
            _save_incident(inc, incidents_dir)

    overall = "OK"
    if any(r.level == "FAIL" for r in reports): overall = "FAIL"
    elif any(r.level == "WARN" for r in reports): overall = "WARN"

    digest = DigestSummary(lookback=lookback, min_priority=min_prio, overall=overall, reports=reports)
    text = render_digest(digest)

    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(digest.model_dump(), ensure_ascii=False, indent=2))

    return digest, text
