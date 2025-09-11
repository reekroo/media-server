# mcp/rpc_methods/logs.py

import logging
import asyncio
from pathlib import Path
from mcp.context import AppContext
from functions.logs.collector import LogCollector

log = logging.getLogger(__name__)

async def build_digest(app: AppContext, config_name: str) -> str:
    log.info(f"Building logs digest for config '{config_name}'")
    cfg = app.settings.logs
    if not cfg or not cfg.enabled: 
        return "Logs digest is disabled or not configured."

    collector = LogCollector()
    tasks = []
    
    # --- ИСПРАВЛЕНИЕ ЗДЕСЬ ---
    # Преобразуем Pydantic-объект в словарь перед перебором
    for name, params_dict in cfg.components.model_dump().items():
    # --- КОНЕЦ ИСПРАВЛЕНИЯ ---
        task = collector.analyze_directory(
            log_dir=Path(params_dict["log_dir"]),
            patterns=params_dict.get("error_patterns", []),
            lookback_hours=cfg.lookback_hours
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    
    warn_reports = [res.model_dump() for res in results if res.status == "WARN"]
    
    summary_text: str
    if not warn_reports:
        summary_text = "All monitored components are nominal. No new errors found in logs."
    else:
        summary_text = await app.ai_service.digest(
            kind='logs',
            params={'reports': warn_reports}
        )
    
    return cfg.render_template.format(summary=summary_text)