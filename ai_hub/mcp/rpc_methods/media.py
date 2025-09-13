from ..context import AppContext
from functions.media.collector import collect_new_titles
from functions.media.titles import list_movie_titles_async
from core.logging import setup_logger, LOG_FILE_PATH

log = setup_logger(__name__, LOG_FILE_PATH)

MEDIA_DISABLED = "🟥 Media digest is disabled or not configured."
NO_NEW = "🟪 No new media and no recommendations to send."

def _render_media_digest(new_titles: list[str], recommend_text: str) -> str:
    parts = []
    if new_titles:
        parts.append("✨ New additions:\n- " + "\n- ".join(new_titles))
    if recommend_text:
        parts.append("🎯 Suggestions for you:\n" + recommend_text.strip())
    return "\n\n".join(parts).strip()

async def build_digest(app: AppContext, config_name: str) -> str:
    log.info(f"Building media digest for config '{config_name}'")
    cfg = app.settings.media
    if not cfg or not cfg.enabled: return MEDIA_DISABLED

    new_titles = await collect_new_titles(
        root=cfg.root, state_path=cfg.state_path,
        include_ext=cfg.include_ext, max_depth=cfg.max_depth
    )
    all_titles = await list_movie_titles_async(cfg.root)
    
    recommend_text = ""
    if all_titles:
        recommend_text = await app.ai_service.digest(
            kind='movies',
            params={"titles": all_titles[:600], "prefs": cfg.recommender.model_dump()}
        )

    if not new_titles and not recommend_text:
        return NO_NEW
    
    return _render_media_digest(new_titles=new_titles, recommend_text=recommend_text)