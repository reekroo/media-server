from __future__ import annotations
from pathlib import Path
import json

def snapshot(root: Path, *, exts: set[str], max_depth: int = 6) -> dict[str,str]:
    items: dict[str,str] = {}
    if not root.exists():
        return items
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts:
            rel = str(p.relative_to(root))
            if rel.count("/") > (max_depth - 1):
                continue
            st = p.stat()
            sig = f"{st.st_size}:{int(st.st_mtime)}"
            items[rel] = sig
    return items

def diff(prev: dict[str,str], curr: dict[str,str]) -> list[str]:
    return [k for k, sig in curr.items() if prev.get(k) != sig]

def load_state(path: Path) -> dict[str,str]:
    return json.loads(path.read_text()) if path.exists() else {}

def save_state(path: Path, snap: dict[str,str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snap, ensure_ascii=False, indent=2))
