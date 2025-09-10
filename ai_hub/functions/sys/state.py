# functions/sys/state.py
import aiofiles
from pathlib import Path

from .model import DigestSummary, Incident

async def save_incident(incident: Incident, incidents_dir: Path) -> None:
    incidents_dir.mkdir(parents=True, exist_ok=True)
    file_path = incidents_dir / f"{incident.id}.json"
    async with aiofiles.open(file_path, "w", encoding="utf-8") as f:
        await f.write(incident.model_dump_json(indent=2))

async def save_digest_state(digest: DigestSummary, state_path: Path) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(state_path, "w", encoding="utf-8") as f:
        await f.write(digest.model_dump_json(indent=2))