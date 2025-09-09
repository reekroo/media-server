from __future__ import annotations
import json
import textwrap
from .base import TopicHandler


_SYS_HINT = (
    "You are a seismology assistant. Earthquake prediction is not reliable—do NOT claim forecasts. "
    "Provide an assessment from recent events: magnitude distribution, clusters, trend, "
    "qualitative aftershock likelihood, and an attention level (low/medium/high) with rationale."
)

class QuakesAssessment(TopicHandler):
    def build_prompt(self, payload: dict) -> str:
        payload_json = json.dumps(payload or {}, ensure_ascii=False)
        return textwrap.dedent(f"""
            {_SYS_HINT}
            
            IMPORTANT: Format your response using simple Markdown. Use asterisks for bold section titles (*Trend Summary*).
            
            Data JSON follows; structure may vary but includes 'events' with ts/mag/lat/lon/depth.

            {payload_json}

            Output sections:
            *Trend Summary* (magnitudes & frequency)
            *Spatial Clusters* (if any)
            *Aftershock Likelihood* (low/med/high) with caveat
            *Attention Level* and a brief why            
        """).strip()
    
    def postprocess(self, llm_text: str) -> str:
        return (llm_text or "").strip()