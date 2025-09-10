from __future__ import annotations
import json

from .base import TopicHandler

_HINT = (
    "You are a reliability assistant. Explain the incident to a technical user in plain language. "
    "Do NOT invent facts. Base your explanation ONLY on provided artifacts. Provide: "
    "1) What happened, 2) Likely cause(s), 3) What to do next (2–4 concrete steps)."
)

class ClarifyIncident(TopicHandler):
    def build_prompt(self, payload: dict) -> str:
        inc = payload.get("incident", {})
        last_digest = payload.get("last_digest")
        inc_json = json.dumps(inc, ensure_ascii=False)
        
        prompt = (
            f"{_HINT}\n\n"
            "IMPORTANT: Format your response using simple Markdown. Use asterisks for bold section titles (*What Happened*).\n\n"
            f"Incident JSON:\n{inc_json}\n"
        )
        
        if last_digest:
            prompt += f"\nLast digest JSON:\n{json.dumps(last_digest, ensure_ascii=False)}\n"
        
        return prompt
    
    def postprocess(self, llm_text: str) -> str:
        return (llm_text or "").strip()