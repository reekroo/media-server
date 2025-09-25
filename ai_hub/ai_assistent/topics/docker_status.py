from __future__ import annotations
import textwrap
import json

from .base import TopicHandler

class DockerStatusTopic(TopicHandler):
    def build_prompt(self, payload: dict) -> str:
        reports = payload.get("reports", []) or []
        meta = payload.get("meta", {}) or {}
        reports_json = json.dumps(reports, indent=2, ensure_ascii=False)
        meta_json = json.dumps(meta, ensure_ascii=False)

        return textwrap.dedent(f"""
            You are an SRE assistant preparing a Telegram message (Markdown only, no HTML, no code fences).
            Input JSON contains UNHEALTHY containers only (if any). Healthy containers are omitted.

            GOAL:
            Produce a compact, scannable *Docker Status Digest* with:
            - header,
            - issues section (if any),
            - final summary.

            ICON RULES:
              running -> ✅
              unhealthy/restarting/paused -> ⚠️
              exited/dead -> 🛑

            OUTPUT FORMAT (STRICT):
            1) First line: "🐳 *Docker Status Digest*"
            2) Second line: "Overall: <EMOJI> <STATUS> (<ISSUES_COUNT> issues)"
               - if reports is empty: STATUS must be "OK" with ✅ and "(0 issues)".
            3) Blank line.
            4) If reports not empty:
                 "🚨 *Issues (<ISSUES_COUNT>):*"
                 Then for EACH report print a compact block, one after another:
                   "<ICON> *<name>* — <STATE_UPPER>"
                   "<one-line cause/summary>"
                   (optionally) "• `<health/status sample>`"  (<= 160 chars)
                 Expected report fields (when present): name/container/id, state, status,
                 restarts, exit_code, uptime, health_msg. Show what's available; avoid redundancy.
            5) Final line (always present):
                 "📊 Summary: <ISSUES_COUNT> need attention."
                 If 'meta.ignored_count' > 0, append:
                 " Ignored: <ignored_count>."

            WRITING STYLE:
            - Short, factual, neutral. Each line <= ~120 chars.
            - Use inline code for short samples only (backticks). No code blocks.
            - Do NOT invent containers or numbers; rely on JSON.

            Reports JSON:
              {reports_json}

            Meta JSON:
              {meta_json}
        """).strip()

    def postprocess(self, llm_text: str) -> str:
        text = (llm_text or "").strip()
        if not text:
            return "🐳 *Docker Status Digest*\nOverall: ✅ OK (0 issues)"
        return text
