import asyncio
from typing import List

from ...context import AppContext
from .processor import NewsSectionProcessor
from .models import SectionParams
from core.logging import setup_logger, LOG_FILE_PATH

log = setup_logger(__name__, LOG_FILE_PATH)

async def build(app: AppContext, config_name: str, section: str | None = None, count: int | None = None) -> List[str]:
    log.info(f"Building digest for config '{config_name}'")
    
    cfg = getattr(app.settings, config_name)
    if not cfg or not cfg.enabled:
        msg = f"Digest '{config_name}' is disabled or not configured."
        log.warning(msg)
        return [msg]

    tasks = []
    for sec_name, section_settings in cfg.feeds.items():
        if section and section != sec_name:
            continue

        params = SectionParams(
            name=sec_name,
            urls=section_settings.urls,
            fetch_limit=section_settings.fetch_limit,
            section_limit=count if count is not None else section_settings.section_limit,
            render_template=section_settings.render_template,
            generate_image=section_settings.generate_image
        )
        
        processor = NewsSectionProcessor(app, cfg.ai_topic, params)
        tasks.append(processor.process())

    results = await asyncio.gather(*tasks)
    final_messages = [msg for msg in results if msg]

    if not final_messages:
        log.info(f"No messages were generated for digest '{config_name}'.")

    return final_messages