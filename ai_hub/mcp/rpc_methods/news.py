from ..context import AppContext
from functions.feeds.feed_collector import FeedCollector
from core.logging import setup_logger, LOG_FILE_PATH

log = setup_logger(__name__, LOG_FILE_PATH)

async def build_digest(app: AppContext, config_name: str, section: str | None = None, count: int | None = None) -> str:
    log.info(f"Building digest for config '{config_name}'")
    
    cfg = getattr(app.settings, config_name)
    if not cfg or not cfg.enabled:
        msg = f"Digest '{config_name}' is disabled or not configured."
        log.warning(msg)
        return msg

    all_items = []
    processed_sections = []
    
    async with FeedCollector() as collector:
        for sec_name, urls_list in cfg.feeds.items():
            if section and section != sec_name:
                continue

            items = await collector.collect(urls=urls_list, max_items=cfg.max_items)
            if items:
                all_items.extend(items)
                processed_sections.append(sec_name)

    if not all_items:
        return f"✅ Digest '{config_name}' successfully built with no new items."

    params = {
        'items': [item.__dict__ for item in all_items],
        'section': section or ", ".join(processed_sections),
        'count': count
    }

    summary_text = await app.ai_service.digest(
        kind=cfg.ai_topic,
        params=params
    )

    final_section_name = (section or "General").capitalize()
    return cfg.render_template.format(section=final_section_name, summary=summary_text)