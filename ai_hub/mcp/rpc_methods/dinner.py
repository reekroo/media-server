import logging

from ..context import AppContext

log = logging.getLogger(__name__)

async def build_digest(app: AppContext, config_name: str) -> str:
    log.info(f"Building dinner digest for config '{config_name}'")
    cfg = app.settings.dinner
    if not cfg or not cfg.enabled: return "Dinner digest is disabled or not configured."

    summary_text = await app.ai_service.digest(
        kind='dinner',
        params=cfg.model_dump()
    )
    return cfg.render_template.format(summary=summary_text)