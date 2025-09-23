from pathlib import Path

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

async def build_brief(app: AppContext, config_name: str) -> str:
    log.info(f"Building daily brief for config '{config_name}'")
    cfg = app.settings.daily
    if not cfg:
        return DAILY_CONFIG_NOT_FOUND

    weather_payload = await read_json_async(Path(cfg.weather_json))
    quakes_payload = await read_json_async(Path(cfg.quakes_json))

    weather_text = ""
    if weather_payload:
        weather_text = await app.ai_service.digest(kind="weather", params=weather_payload)

    quakes_text = ""
    if getattr(cfg, "include_quakes", False) and quakes_payload:
        quakes_text = await app.ai_service.digest(kind="quakes", params=quakes_payload)

    parts = []

    weather = _section("🌤️ *Weather*", weather_text)
    if weather:
        parts.append(weather)

    quakes = _section("🌍 *Earthquakes*", quakes_text)
    if quakes:
        parts.append(quakes)

    if not parts:
        return DATA_UNAVAILABLE

    return "\n\n".join(parts).strip()
