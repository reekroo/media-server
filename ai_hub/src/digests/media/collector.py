from __future__ import annotations
from pathlib import Path
from typing import Sequence, List
from ...io.media_index import snapshot_async, diff, load_state_async, save_state_async

class NewTitlesCollector:
    def __init__(self, state_path: Path, include_ext: Sequence[str], max_depth: int = 6):
        self.state_path = state_path
        self.extensions = {ext.lower() for ext in include_ext}
        self.max_depth = max_depth

    async def collect(self, root: Path) -> List[str]:
        previous_state = await load_state_async(self.state_path)
        current_state = await snapshot_async(root, exts=self.extensions, max_depth=self.max_depth)
        
        new_relative_paths = diff(previous_state, current_state)
        
        await save_state_async(self.state_path, current_state)
        
        titles = {Path(rel).stem for rel in new_relative_paths if Path(rel).stem}
        
        return sorted(list(titles))

async def collect_new_titles_async(
    *, root: Path, state_path: Path, include_ext: Sequence[str], max_depth: int = 6
) -> list[str]:
    collector = NewTitlesCollector(state_path, include_ext, max_depth)
    return await collector.collect(root)