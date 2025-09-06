from __future__ import annotations
import json
from .base import TopicHandler

_SYS_HINT = (
    "You are a seismology assistant. Earthquake prediction is not reliable—do NOT claim forecasts. "
    "Provide an assessment from recent events: magnitude distribution, clusters, trend, "
    "qualitative aftershock likelihood, and an attention level (low/medium/high) with rationale."
)

class QuakesAssessment(TopicHandler):
    def build_prompt(self, payload: dict) -> str:
        payload_json = json.dumps(payload or {}, ensure_ascii=False)
        return (
            f"{_SYS_HINT}\n"
            "Data JSON follows; structure may vary but includes 'events' with ts/mag/lat/lon/depth.\n"
            f"{payload_json}\n"
            "Output sections:\n"
            "1) Trend summary (magnitudes & frequency)\n"
            "2) Spatial clusters (if any)\n"
            "3) Aftershock likelihood qualitatively (low/med/high) with caveat\n"
            "4) Attention level and a brief why\n"
        )
    def postprocess(self, llm_text: str) -> str:
        return (llm_text or "").strip()
