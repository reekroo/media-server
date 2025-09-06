from __future__ import annotations
from pathlib import Path
from typing import Sequence
from ...io.media_index import snapshot, diff, load_state, save_state

def collect_new_titles(*, root: Path, state_path: Path, include_ext: Sequence[str], max_depth: int = 6) -> list[str]:
    exts = {e.lower() for e in include_ext}
    prev = load_state(state_path)
    curr = snapshot(root, exts=exts, max_depth=max_depth)
    new_rel_paths = diff(prev, curr)
    # Обновляем state
    save_state(state_path, curr)
    # Титры — это stem без расширения из относительного пути
    titles = []
    for rel in new_rel_paths:
        stem = Path(rel).stem
        if stem:
            titles.append(stem)
    # dedupe + sort
    return sorted(set(titles))
