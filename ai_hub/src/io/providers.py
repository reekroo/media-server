from __future__ import annotations
from pathlib import Path
import asyncio

def _list_movie_titles_sync(root: Path) -> list[str]:
    exts = {".mkv", ".mp4", ".avi", ".mov"}
    titles: set[str] = set()
    if not root.exists():
        return []
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts:
            titles.add(p.stem)
    return sorted(titles)

async def list_movie_titles_async(root: Path) -> list[str]:
    return await asyncio.to_thread(_list_movie_titles_sync, root)