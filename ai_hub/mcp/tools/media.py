from __future__ import annotations
import asyncio
from pathlib import Path
import tomllib
from src.core.settings import Settings
from src.core.agents.factory import agent_factory
from src.core.router import Orchestrator
from src.topics.movies import MoviesRecommend
from src.digests.media.collector import collect_new_titles
from src.digests.media.recommender import build_media_recommendations
from src.digests.media.templates import render_media_digest

def _orch() -> Orchestrator:
    s = Settings()
    agent = agent_factory(api_key=s.GEMINI_API_KEY)
    topics = {"movies.recommend": MoviesRecommend()}
    return Orchestrator(agent, topics)

def media_digest(config: str = "configs/media.toml") -> str:
    """
    MCP tool: media.digest
    params:
      - config: путь к TOML конфигу медиадайджеста.
    returns: str — сводка (новое + рекомендации).
    """
    s = Settings()
    cfg = tomllib.loads(Path(config).read_text("utf-8")) if Path(config).exists() else {}
    root = Path(cfg.get("root", str(s.MOVIES_ROOT)))
    include_ext = cfg.get("include_ext", [".mkv",".mp4",".avi",".mov"])
    state_path = Path(cfg.get("state_path", "state/media_index.json"))
    max_depth = int(cfg.get("max_depth", 6))
    prefs = cfg.get("recommender", {})
    new_titles = collect_new_titles(root=root, state_path=state_path, include_ext=include_ext, max_depth=max_depth)

    orch = _orch()
    async def _run():
        rec_text = await build_media_recommendations(orch, root=root, prefs=prefs, cap=cfg.get("cap", 600))
        return render_media_digest(new_titles=new_titles, recommend_text=rec_text, soon_text=None)
    return asyncio.run(_run())
