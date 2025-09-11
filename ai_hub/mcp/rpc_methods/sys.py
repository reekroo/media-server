import logging

from ..context import AppContext
from ..logic import sys_rules, sys_templates

from functions.sys.collector import get_unit_status, get_unit_logs
from functions.sys.state import save_incident, save_digest_state
from functions.sys.model import DigestSummary, UnitReport

log = logging.getLogger(__name__)

async def build_digest(app: AppContext, config_name: str) -> None:
    log.info(f"Executing job: sys.build_digest for config '{config_name}'")
    cfg = app.settings.sys
    if not cfg or not cfg.enabled: return

    reports: list[UnitReport] = []
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

    message = sys_templates.render_digest(digest)
    channel = app.channel_factory.get_channel(cfg.to)
    await channel.send(destination=cfg.destination, content=message)
    log.info(f"Digest '{config_name}' sent successfully.")