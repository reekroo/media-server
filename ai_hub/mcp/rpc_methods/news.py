import logging
import tomllib
from pathlib import Path

# --- Правильные абсолютные импорты ---
from ..context import AppContext
from functions.feeds.feed_collector import FeedCollector

log = logging.getLogger(__name__)

async def build_digest(app: AppContext, config_name: str, section: str | None = None) -> None:
    log.info(f"Executing job: news.build_digest for config '{config_name}'")
    
    cfg = getattr(app.settings, config_name)
    if not cfg or not cfg.enabled:
        log.warning(f"Digest '{config_name}' is disabled or not configured. Skipping.")
        return

    async with FeedCollector() as collector:
        for sec_name, urls_list in cfg.feeds.items():
            if section and section != sec_name:
                continue

            log.info(f"Collecting feeds for '{config_name}/{sec_name}'...")
            items = await collector.collect(
                urls=urls_list,
                max_items=cfg.max_items
            )
            if not items:
                log.info(f"No new items found for '{config_name}/{sec_name}'.")
                continue

            log.info(f"Found {len(items)} items. Summarizing with AI topic '{cfg.ai_topic}'...")
            summary_text = await app.ai_service.digest(
                kind=cfg.ai_topic,
                params={'items': [item.__dict__ for item in items], 'section': sec_name}
            )

            message = cfg.render_template.format(section=sec_name.capitalize(), summary=summary_text)
            
            log.info(f"Sending digest '{config_name}/{sec_name}' to channel '{cfg.to}'...")
            channel = app.channel_factory.get_channel(cfg.to)
            await channel.send(destination=cfg.destination, content=message)
            log.info(f"Digest '{config_name}/{sec_name}' sent successfully.")