from __future__ import annotations
import textwrap
import json

from .base import TopicHandler

class LogAnalysisTopic(TopicHandler):
    def build_prompt(self, payload: dict) -> str:
        reports = payload.get("reports", [])
        reports_json = json.dumps(reports, indent=2, ensure_ascii=False)

        return textwrap.dedent(f"""
            You are an SRE (Site Reliability Engineer) assistant.
            Analyze the following log analysis reports from several system components for the last 24 hours.
            The status is 'WARN' if any error patterns were found in recent log files.

            For each component, provide a one-sentence summary of its health.
            If the status is 'WARN', briefly mention the nature of the errors based on the samples.
            Conclude with a single, overall health status: OK ✅, WARN ⚠️, or ERROR 🛑.              
                               
            IMPORTANT, OUTPUT FORMAT (STRICT):
            - Use simple Markdown ONLY (no HTML, no code fences).
            - Component Name: *Status* - One-sentence summary.
            - ...
            *Overall: OK, WARN, or ERROR*

            Reports JSON: 
                {reports_json}
        """).strip()

    def postprocess(self, llm_text: str) -> str:
        return (llm_text or "").strip()