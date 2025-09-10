import json
from pathlib import Path
from typing import Any, Dict
import aiofiles

async def read_json_async(path: Path) -> Dict[str, Any]:
    """Асинхронно читает и парсит JSON-файл."""
    if not path or not path.exists():
        return {}
    try:
        async with aiofiles.open(path, "r", encoding="utf-8") as f:
            content = await f.read()
            return json.loads(content)
    except (IOError, json.JSONDecodeError):
        return {}