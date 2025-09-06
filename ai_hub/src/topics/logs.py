from __future__ import annotations
import json
from .base import TopicHandler

class LogAnalysisTopic(TopicHandler):
    def build_prompt(self, payload: dict) -> str:
        reports = payload.get("reports", [])
        reports_json = json.dumps(reports, indent=2, ensure_ascii=False)

        return (
            "You are an SRE (Site Reliability Engineer) assistant. "
            "Analyze the following log analysis reports from several system components for the last 24 hours. "
            "The status is 'WARN' if any error patterns were found in recent log files.\n\n"
            "For each component, provide a one-sentence summary of its health. "
            "If the status is 'WARN', briefly mention the nature of the errors based on the samples.\n\n"
            "Conclude with a single, overall health status: OK, WARN, or ERROR.\n\n"
            f"Reports JSON:\n{reports_json}\n\n"
            "Output format:\n"
            "- Component Name: [Status] - One-sentence summary.\n"
            "- ...\n"
            "Overall: [OK, WARN, or ERROR]"
        )

    def postprocess(self, llm_text: str) -> str:
        return (llm_text or "").strip()