from __future__ import annotations
from ..context import AppContext
from functions.media.collector import collect_new_titles
from functions.media.titles import list_movie_titles_async
from core.logging import setup_logger, LOG_FILE_PATH

from ..domain.media_rules import group_new_titles
from ..domain.media_templates import render_media_digest

log = setup_logger(__name__, LOG_FILE_PATH)

MEDIA_DISABLED = "🟥 Media digest is disabled or not configured."
NO_NEW = "🟪 No new media and no recommendations to send."

async def build_digest(app: AppContext, config_name: str) -> str:
    log.info(f"Building media digest for config '{config_name}'")
    cfg = app.settings.media
    if not cfg or not cfg.enabled:
        return MEDIA_DISABLED

    raw_new_titles = await collect_new_titles(
        root=cfg.root,
        state_path=cfg.state_path,
        include_ext=cfg.include_ext,
        max_depth=cfg.max_depth,
    )
    new_lines = group_new_titles(raw_new_titles)

    recommend_text = ""
    limit = cfg.recommender.max_titles_for_recommender
    all_titles = await list_movie_titles_async(cfg.root)
    
    if all_titles:
        recommend_text = await app.ai_service.digest(
            kind="movies",
            params={"titles": all_titles[:limit], "prefs": cfg.recommender.model_dump()},
        )

    if not new_lines and not recommend_text:
        return NO_NEW

    return render_media_digest(new_lines, recommend_text)