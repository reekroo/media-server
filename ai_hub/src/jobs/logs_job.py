# logs_job.py
from __future__ import annotations
import tomllib
from pathlib import Path
from typing import TYPE_CHECKING
import asyncio

if TYPE_CHECKING:
    from ..app import App

from ..digests.logs.collector import LogCollector
from ..digests.logs.templates import render_log_digest

async def run(app: App, config_path_override: str | None = None) -> list[str]:
    svc = app.services
    config_path = Path(config_path_override) if config_path_override else svc.settings.BASE_DIR / "configs" / "logs.toml"
    if not config_path.exists():
        return ["Log digest config not found."]

    cfg = tomllib.loads(config_path.read_text("utf-8"))
    if not cfg.get("enabled", False):
        return []

    lookback = cfg.get("lookback_hours", 24)
    components = cfg.get("components", {})

    collector = LogCollector()
    tasks = []
    for name, params in components.items():
        task = collector.analyze_directory(
            log_dir=Path(params["log_dir"]),
            patterns=params["error_patterns"],
            lookback_hours=lookback
        )
        tasks.append(task)

    results = await asyncio.gather(*tasks)

    warn_reports = [res.model_dump() for res in results if res.status == "WARN"]

    if not warn_reports:
        summary = "All monitored components are nominal. No new errors found in logs."
    else:
        summary = await svc.orchestrator.run("logs.analyze", {"reports": warn_reports})

    return [render_log_digest(summary)]
