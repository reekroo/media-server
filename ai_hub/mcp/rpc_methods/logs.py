import asyncio
from pathlib import Path

from mcp.context import AppContext
from functions.logs.collector import LogCollector
from core.logging import setup_logger, LOG_FILE_PATH

log = setup_logger(__name__, LOG_FILE_PATH)

LOGS_DISABLED = "🟥 Logs digest is disabled or not configured."
LOGS_ALL_NORMAL = "✅ All monitored components are nominal. No new errors found in logs."

async def build_digest(app: AppContext, config_name: str) -> str:
    log.info(f"Building logs digest for config '{config_name}'")
    cfg = app.settings.logs
    if not cfg or not cfg.enabled:
        return LOGS_DISABLED

    collector = LogCollector()
    tasks = []

    for name, params_dict in cfg.components.model_dump().items():
        task = collector.analyze_directory(
            log_dir=Path(params_dict["log_dir"]),
            patterns=params_dict.get("error_patterns", []),
            lookback_hours=cfg.lookback_hours,
        )
        tasks.append(task)

    results = await asyncio.gather(*tasks)

    warn_reports = [res.model_dump() for res in results if res.status == "WARN"]
    ok_components = [res.component for res in results if res.status != "WARN"]

    if not warn_reports:
        return cfg.render_template.format(summary=LOGS_ALL_NORMAL)

    summary_text: str = await app.ai_service.digest(
        kind="logs",
        params={
            "reports": warn_reports,
            "ok_components": ok_components,
            "meta": {
                "issues_count": len(warn_reports),
                "healthy_count": len(ok_components),
                "lookback_hours": cfg.lookback_hours,
            },
        },
    )

    return cfg.render_template.format(summary=summary_text)
