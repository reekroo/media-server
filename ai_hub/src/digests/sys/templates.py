from __future__ import annotations
from typing import Iterable
from .model import DigestSummary, UnitReport, Issue

def _badge(level: str) -> str:
    return {"OK": "✅", "WARN": "⚠️", "FAIL": "🛑"}.get(level, "❔")

def _fmt_report(r: UnitReport) -> str:
    head = f"{_badge(r.level)} {r.unit} — {r.level}"
    details = [f"active={r.status.active}, restarts={r.status.restarts}"]
    
    if r.issues:
        unique_issues = sorted(list(set(
            (i.category, i.pattern) for i in r.issues
        )))
        issues_txt = ", ".join(f"{cat}({pat})" for cat, pat in unique_issues)
        details.append(f"issues: {issues_txt}")

    if r.samples:
        samples = "\n".join(f"  • {ln[:160]}" for ln in r.samples[:3])
        details.append("samples:\n" + samples)
        
    body = "\n".join(details)
    return f"{head}\n{body}" if body else head


def render_digest(d: DigestSummary) -> str:
    lines = [f"🖥️ System status (since {d.lookback}, min={d.min_priority}) — overall: {d.overall}", ""]
    ordered: Iterable[UnitReport] = sorted(d.reports, key=lambda x: {"FAIL":0,"WARN":1,"OK":2}[x.level])
    for r in ordered:
        lines.append(_fmt_report(r)); lines.append("")
    return "\n".join(lines).rstrip()