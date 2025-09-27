import asyncio
from pathlib import Path
from typing import Any, List

from ..context import AppContext
from functions.local_data.reader import read_json_async
from core.logging import setup_logger, LOG_FILE_PATH

log = setup_logger(__name__, LOG_FILE_PATH)

DAILY_CONFIG_NOT_FOUND = "🟥 Daily config not found."
DATA_UNAVAILABLE = "🟨 Data is currently unavailable."

def _section(title: str, body: str | None) -> str:
    body = (body or "").strip()
    if not body or body == DATA_UNAVAILABLE:
        return ""
    return f"{title}\n\n{body}"

async def _get_weather_section(app: AppContext, cfg: Any) -> str:
    try:
        payload = await read_json_async(Path(cfg.weather_json))
        if not payload: return ""
        weather_text = await app.ai_service.digest(kind="weather", params=payload)
        return _section("🌤️ *Weather*", weather_text)
    except Exception as e:
        log.error(f"Failed to process weather section: {e}", exc_info=True)
        return ""

async def _get_quakes_section(app: AppContext, cfg: Any) -> str:
    if not getattr(cfg, "include_quakes", False): return ""
    try:
        payload = await read_json_async(Path(cfg.quakes_json))
        if not payload: return ""
        quakes_text = await app.ai_service.digest(kind="quakes", params=payload)
        return _section("🌍 *Earthquakes*", quakes_text)
    except Exception as e:
        log.error(f"Failed to process quakes section: {e}", exc_info=True)
        return ""

async def build(app: AppContext, config_name: str) -> str:
    log.info(f"Building daily brief for config '{config_name}'")
    cfg = app.settings.daily
    if not cfg:
        return DAILY_CONFIG_NOT_FOUND

    tasks = [_get_weather_section(app, cfg), _get_quakes_section(app, cfg)]
    results: List[str] = await asyncio.gather(*tasks)
    final_parts = [part for part in results if part]

    if not final_parts:
        return DATA_UNAVAILABLE

    return "\n\n".join(final_parts).strip()