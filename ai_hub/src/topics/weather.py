from __future__ import annotations
import json
from .base import TopicHandler

_SYS_HINT = (
    "You are a concise meteorology assistant. Summarize today's weather for a tech user. "
    "Be practical: temperatures, feels-like, wind, precipitation, notable alerts. "
    "Prefer 1–2 short sentences plus 2–4 compact bullets if needed."
)

class WeatherSummary(TopicHandler):
    def build_prompt(self, payload: dict) -> str:
        payload_json = json.dumps(payload or {}, ensure_ascii=False)
        return (
            f"{_SYS_HINT}\n"
            "Input JSON (keys may include ts, temp_c, feels_like_c, humidity, wind_mps, "
            "precip_mm_last_hour, alerts[]):\n"
            f"{payload_json}\n"
            "Output in plain text (no JSON):\n"
            "- One-liner summary.\n"
            "- Optional bullets for umbrella/heat/wind and alerts.\n"
        )
    def postprocess(self, llm_text: str) -> str:
        return (llm_text or "").strip()
