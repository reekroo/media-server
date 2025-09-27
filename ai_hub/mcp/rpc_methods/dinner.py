from typing import Optional
from ..context import AppContext
from core.logging import setup_logger, LOG_FILE_PATH

log = setup_logger(__name__, LOG_FILE_PATH)

DIGEST_DISABLED = "🟥 Dinner digest is disabled or not configured."

async def build(app: AppContext, config_name: str, count: Optional[int] = None) -> str:
    log.info(f"Building dinner digest for config '{config_name}'")
    cfg = app.settings.dinner
    if not cfg or not cfg.enabled:
        return DIGEST_DISABLED

    params_for_ai = {"preferences": cfg.model_dump(), "count": count}
    summary_text = await app.ai_service.digest(kind='dinner', params=params_for_ai)
    return cfg.render_template.format(summary=summary_text)