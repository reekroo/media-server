import logging

from ..context import AppContext
from functions.feeds.feed_collector import FeedCollector

log = logging.getLogger(__name__)

async def build_digest(app: AppContext, config_name: str, section: str | None = None) -> str:
    log.info(f"Building digest for config '{config_name}'")
    
    cfg = getattr(app.settings, config_name)
    if not cfg or not cfg.enabled:
        msg = f"Digest '{config_name}' is disabled or not configured."
        log.warning(msg)
        return msg

    full_digest_text = ""
    async with FeedCollector() as collector:
        for sec_name, urls_list in cfg.feeds.items():
            if section and section != sec_name: continue

            items = await collector.collect(urls=urls_list, max_items=cfg.max_items)
            if not items: continue

            summary_text = await app.ai_service.digest(
                kind=cfg.ai_topic,
                params={'items': [item.__dict__ for item in items], 'section': sec_name}
            )
            message = cfg.render_template.format(section=sec_name.capitalize(), summary=summary_text)
            full_digest_text += message + "\n\n"

    if not full_digest_text:
        return f"✅ Digest '{config_name}' successfully built with no output."

    return full_digest_text.strip()