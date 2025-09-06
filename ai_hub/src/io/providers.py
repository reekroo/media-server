from __future__ import annotations
from pathlib import Path

def list_movie_titles(root: Path) -> list[str]:
    exts = {".mkv", ".mp4", ".avi", ".mov"}
    titles: set[str] = set()
    if not root.exists():
        return []
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts:
            titles.add(p.stem)
    return sorted(titles)
