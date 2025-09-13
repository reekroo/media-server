from ..context import AppContext
from core.logging import setup_logger, LOG_FILE_PATH

log = setup_logger(__name__, LOG_FILE_PATH)

DIGEST_DISABLED = "🟥 Dinner digest is disabled or not configured."

async def build_digest(app: AppContext, config_name: str) -> str:
    log.info(f"Building dinner digest for config '{config_name}'")
    cfg = app.settings.dinner
    if not cfg or not cfg.enabled: return DIGEST_DISABLED

    summary_text = await app.ai_service.digest(
        kind='dinner',
        params=cfg.model_dump()
    )
    return cfg.render_template.format(summary=summary_text)