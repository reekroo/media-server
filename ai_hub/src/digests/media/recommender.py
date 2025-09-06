from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
from ...core.router import Orchestrator
from ...io.providers import list_movie_titles_async

class MediaRecommender:
    def __init__(self, orchestrator: Orchestrator):
        self._orchestrator = orchestrator

    async def build(
        self,
        root: Path,
        prefs: Dict[str, Any],
        cap: int = 600
    ) -> str:
        titles = await list_movie_titles_async(root)
        
        payload = {
            "titles": titles[:cap],
            "prefs": prefs or {}
        }
        
        return await self._orchestrator.run("movies.recommend", payload)

async def build_media_recommendations(
    orch: Orchestrator,
    *,
    root: Path,
    prefs: Dict[str, Any],
    cap: int = 600
) -> str:
    recommender = MediaRecommender(orch)
    return await recommender.build(root, prefs, cap)