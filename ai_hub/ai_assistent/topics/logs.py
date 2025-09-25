from __future__ import annotations
import textwrap
import json

from .base import TopicHandler

class LogAnalysisTopic(TopicHandler):
    def build_prompt(self, payload: dict) -> str:
        """
        Produces a strict, Telegram-safe Markdown outline for the logs digest:
        - Header with overall status
        - 🚨 Issues: one compact block per problematic component
        - ✅ Healthy: bullet list of ok components
        - 📊 Summary line at the end
        """
        reports = payload.get("reports", []) or []
        ok_components = payload.get("ok_components", []) or []
        meta = payload.get("meta", {}) or {}

        reports_json = json.dumps(reports, indent=2, ensure_ascii=False)
        ok_json = json.dumps(ok_components, ensure_ascii=False)

        return textwrap.dedent(f"""
            You are an SRE assistant preparing a Telegram message.
            You will receive JSON with WARN reports (problematic components) and a list of healthy components.
            Create a concise, highly scannable digest using ONLY simple Markdown (no HTML, no code fences).

            WRITING STYLE:
            - Short, factual, neutral tone. Avoid redundancy.
            - Keep each line under ~120 chars to prevent wrapping issues in Telegram.
            - Escape backticks inside inline code where needed.

            OUTPUT FORMAT (STRICT):
            1) First line: "📊 *Log Analysis Digest*"
            2) Second line: "Overall: <STATUS_EMOJI> <STATUS>"  where STATUS is one of: OK, WARN, ERROR.
            3) Blank line.
            4) If there are issues (reports not empty), print:
               "🚨 *Issues (<ISSUES_COUNT>):*"
               Then for EACH report print a compact block:
               "<ICON> *<component_name>* — <STATUS>"
               "<one-line cause/summary>"
               (optionally) "• `<log sample 1>`"
               (optionally) "• `<log sample 2>`"
               Rules for samples:
                 - at most 2 lines
                 - strip/shorten to <= 160 visible chars
                 - wrap in backticks
            5) If there are healthy components, print:
               "✅ *Healthy (<HEALTHY_COUNT>):*"
               Then each on its own line:
               "• <component_name>" (append " (restarts: N)" only if N>0 and the value is present in the report data)
            6) Final line:
               "📊 Summary: <ISSUES_COUNT> need attention, <HEALTHY_COUNT> healthy."

            ICON RULES:
            - FAIL -> 🛑
            - WARN -> ⚠️
            - otherwise -> ✅

            IMPORTANT CONSTRAINTS:
            - Do NOT use code fences. Only inline code with backticks is allowed.
            - Do NOT invent components. Only use those present in the JSON.
            - Do NOT print raw JSON.
            - If a reason is unclear, infer it briefly from error categories/samples (e.g., "DNS failure", "502 Bad Gateway").

            Inputs:
            - WARN Reports JSON:
              {reports_json}

            - Healthy Components JSON:
              {ok_json}

            - Meta (counts, lookback hours):
              {json.dumps(meta, ensure_ascii=False)}
        """).strip()

    def postprocess(self, llm_text: str) -> str:
        text = (llm_text or "").strip()
        if not text:
            return "📊 *Log Analysis Digest*\nOverall: ✅ OK"
        return text
