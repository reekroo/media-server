from ..context import AppContext
from functions.media.collector import collect_new_titles
from functions.media.titles import list_movie_titles_async

def _render_media_digest(new_titles: list[str], recommend_text: str) -> str:
    """Собирает финальное сообщение для медиа-дайджеста."""
    parts = []
    if new_titles:
        parts.append("✨ New additions:\n- " + "\n- ".join(new_titles))
    
    if recommend_text:
        parts.append("🎯 Suggestions for you:\n" + recommend_text.strip())
        
    return "\n\n".join(parts).strip()

async def build_digest(app: AppContext, config_name: str) -> None:
    """Собирает полный медиа-дайджест: новые файлы + LLM-рекомендации."""
    print(f"Executing job: media.build_digest for config '{config_name}'")

    cfg = app.settings.media
    if not cfg or not cfg.enabled:
        return

    new_titles = await collect_new_titles(
        root=cfg.root,
        state_path=cfg.state_path,
        include_ext=cfg.include_ext,
        max_depth=cfg.max_depth
    )

    all_titles = await list_movie_titles_async(cfg.root)
    
    recommend_text = ""
    if all_titles:
        recommend_text = await app.ai_service.digest(
            kind='movies',
            params={
                "titles": all_titles[:600],
                "prefs": cfg.recommender.model_dump()
            }
        )

    if not new_titles and not recommend_text:
        print("No new media and no recommendations to send.")
        return

    message = _render_media_digest(new_titles=new_titles, recommend_text=recommend_text)

    channel = app.channel_factory.get_channel(cfg.to)
    await channel.send(destination=cfg.destination, content=message)
    print(f"Digest '{config_name}' sent successfully.")