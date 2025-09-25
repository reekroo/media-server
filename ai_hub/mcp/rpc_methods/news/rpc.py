import asyncio
from typing import List

from ...context import AppContext
from .processor import NewsSectionProcessor, create_section_params
from core.logging import setup_logger, LOG_FILE_PATH

log = setup_logger(__name__, LOG_FILE_PATH)

async def build_digest(app: AppContext, config_name: str, section: str | None = None, count: int | None = None) -> List[str]:
    log.info(f"Building digest for config '{config_name}'")
    
    cfg = getattr(app.settings, config_name)
    if not cfg or not cfg.enabled:
        msg = f"Digest '{config_name}' is disabled or not configured."
        log.warning(msg)
        return [msg]

    tasks = []
    for sec_name, section_config in cfg.feeds.items():
        if section and section != sec_name:
            continue
        
        params = create_section_params(sec_name, section_config, cfg, count)
        processor = NewsSectionProcessor(app, cfg, params)
        tasks.append(processor.process())

    log.info(f"Processing {len(tasks)} sections in parallel for '{config_name}'...")
    results = await asyncio.gather(*tasks)

    final_messages = [msg for msg in results if msg]

    if not final_messages:
        log.info(f"No messages were generated for digest '{config_name}'.")

    return final_messages