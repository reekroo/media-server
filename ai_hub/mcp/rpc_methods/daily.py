from pathlib import Path

from mcp.context import AppContext
from functions.local_data.reader import read_json_async

BRIEF_FORMAT = """\
🌤️ **Weather**
{weather}

🌍 **Earthquakes**
{quakes}
"""

async def build_brief(app: AppContext, config_name: str) -> None:
    """Генерирует и отправляет дневной брифинг."""
    print(f"Executing job: daily.build_brief for config '{config_name}'")

    cfg = app.settings.daily
    if not cfg:
        return

    weather_payload = await read_json_async(Path(cfg.weather_json))
    quakes_payload = await read_json_async(Path(cfg.quakes_json))

    weather_text = "Weather data is currently unavailable."
    if weather_payload:
        weather_text = await app.ai_service.digest(kind='weather', params=weather_payload)

    quakes_text = ""
    if cfg.include_quakes and quakes_payload:
        quakes_text = await app.ai_service.digest(kind='quakes', params=quakes_payload)

    brief_content = BRIEF_FORMAT.format(weather=weather_text, quakes=quakes_text).strip()

    channel = app.channel_factory.get_channel(cfg.to)
    await channel.send(destination=cfg.destination, content=brief_content)
    print(f"Job 'daily.build_brief' completed.")