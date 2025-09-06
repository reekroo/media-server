from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
from ...core.router import Orchestrator
from ...io.providers import list_movie_titles

async def build_media_recommendations(
    orch: Orchestrator,
    *,
    root: Path,
    prefs: Dict[str, Any],
    cap: int = 600
) -> str:
    titles = list_movie_titles(root)[:cap]
    payload = {"titles": titles, "prefs": prefs or {}}
    return await orch.run("movies.recommend", payload)
