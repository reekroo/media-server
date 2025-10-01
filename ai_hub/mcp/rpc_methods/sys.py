from ..context import AppContext
from ..domain import sys_rules, sys_templates
from functions.sys.collector import get_unit_status, get_unit_logs
from functions.sys.state import save_incident, save_digest_state
from functions.sys.models import DigestSummary
from core.logging import setup_logger, LOG_FILE_PATH

log = setup_logger(__name__, LOG_FILE_PATH)

SYS_DISABLED = "🟪 System digest is disabled or not configured."

async def build_digest(app: AppContext, config_name: str) -> str:
    log.info(f"Building system digest for config '{config_name}'")
    cfg = app.settings.sys
    if not cfg or not cfg.enabled: return SYS_DISABLED

    reports = []
    for unit_name in cfg.units:
        status = await get_unit_status(unit_name)
        logs = await get_unit_logs(unit_name, lookback=cfg.lookback, min_priority=cfg.min_priority)
        report = sys_rules.classify(status, logs, cfg.patterns.model_dump(), cfg.max_restarts)
        reports.append(report)

        if report.level in ("WARN", "FAIL"):
            incident = sys_rules.create_incident_from_report(report)
            await save_incident(incident, app.settings.STATE_DIR / "incidents")
    
    overall_level = sys_rules.determine_overall_level(reports)
    digest = DigestSummary(lookback=cfg.lookback, min_priority=cfg.min_priority, overall=overall_level, reports=reports)
    await save_digest_state(digest, app.settings.STATE_DIR / "sys_digest.json")
    
    return sys_templates.render_digest(digest)