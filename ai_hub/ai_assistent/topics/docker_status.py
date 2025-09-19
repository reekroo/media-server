from __future__ import annotations
import textwrap
import json

from .base import TopicHandler

class DockerStatusTopic(TopicHandler):
    def build_prompt(self, payload: dict) -> str:
        reports = payload.get("reports", [])
        reports_json = json.dumps(reports, indent=2, ensure_ascii=False)

        return textwrap.dedent(f"""
            You are an SRE (Site Reliability Engineer) assistant.
            Analyze the following status report for Docker containers.
            A container is considered unhealthy if its status is 'restarting', 'dead', or 'exited' with a non-zero exit code.

            For each unhealthy container, provide a one-sentence summary of its problem.
            Conclude with a single, overall health status: OK ✅, WARN ⚠️, or ERROR 🛑.

            IMPORTANT, OUTPUT FORMAT (STRICT):
            - Use simple Markdown ONLY (no HTML, no code fences).
            - Container Name: *Status* - One-sentence summary (e.g., 'Container exited with error code 137').
            - ...
            *Overall: OK, WARN, or ERROR*

            Reports JSON: 
                {reports_json}
        """).strip()

    def postprocess(self, llm_text: str) -> str:
        return (llm_text or "").strip()