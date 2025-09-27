import json

from .base import TopicHandler
from .formatters.base import Formatter
from .formatters.simple_text_formatter import SimpleTextFormatter

_SYS_HINT = (
    "You are a concise meteorology assistant. Summarize today's weather for a tech user. "
    "Be practical: temperatures, feels-like, wind, precipitation, notable alerts."
)

class WeatherSummary(TopicHandler):
    @property
    def formatter(self) -> Formatter:
        return SimpleTextFormatter()

    def build_prompt(self, payload: dict) -> str:
        payload_json = json.dumps(payload or {}, ensure_ascii=False)
        return (
            f"{_SYS_HINT}\n\n"
            "OUTPUT STYLE (STRICT):\n"
            "- First line: a short one-sentence headline (e.g., 'Clear, ~15°C; light wind').\n"
            "- Then 3–5 compact bullets with key facts. Use '-' bullets only.\n"
            "- Avoid empty/unknown fields. Keep lines <= ~120 chars.\n\n"
            "Use simple Markdown only (no HTML, no code fences).\n\n"
            "Input JSON (keys may include ts, temp_c, feels_like_c, humidity, wind_mps, "
            "precip_mm_last_hour, alerts[]):\n"
            f"{payload_json}\n"
        )