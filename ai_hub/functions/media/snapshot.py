from __future__ import annotations
from pathlib import Path
import json
import asyncio
import aiofiles

def _snapshot_sync(root: Path, *, exts: set[str], max_depth: int = 6) -> dict[str, str]:
    items: dict[str, str] = {}
    if not root.exists():
        return items
    
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts:
            try:
                rel = str(p.relative_to(root))
                if rel.count("/") > (max_depth - 1):
                    continue
                st = p.stat()
                sig = f"{st.st_size}:{int(st.st_mtime)}"
                items[rel] = sig
            except FileNotFoundError:
                continue
    
    return items

async def snapshot_async(root: Path, *, exts: set[str], max_depth: int = 6) -> dict[str, str]:
    return await asyncio.to_thread(_snapshot_sync, root, exts=exts, max_depth=max_depth)

def diff(prev: dict[str, str], curr: dict[str, str]) -> list[str]:
    return [k for k, sig in curr.items() if prev.get(k) != sig]

async def load_state_async(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    try:
        async with aiofiles.open(path, "r", encoding="utf-8") as f:
            content = await f.read()
            return json.loads(content)
    except (IOError, json.JSONDecodeError):
        return {}

async def save_state_async(path: Path, snap: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(snap, ensure_ascii=False, indent=2))