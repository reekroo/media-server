from __future__ import annotations
from pathlib import Path
from typing import Sequence, List

from .snapshot import snapshot_async, diff, load_state_async, save_state_async

async def collect_new_titles(
    root: Path, *, state_path: Path, include_ext: Sequence[str], max_depth: int = 6
) -> List[str]:
    previous_state = await load_state_async(state_path)
    current_state = await snapshot_async(root, exts=set(include_ext), max_depth=max_depth)

    new_relative_paths = diff(previous_state, current_state)

    await save_state_async(state_path, current_state)

    titles = {Path(rel).stem for rel in new_relative_paths if Path(rel).stem}
    return sorted(list(titles))