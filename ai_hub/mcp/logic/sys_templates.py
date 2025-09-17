from typing import Iterable

from functions.sys.models import DigestSummary, UnitReport

def _badge(level: str) -> str:
    return {"OK": "✅", "WARN": "⚠️", "FAIL": "🛑"}.get(level, "❔")

def _format_report(r: UnitReport) -> str:
    head = f"{_badge(r.level)} *{r.unit}* — {r.level}"
    details = [f"Status: `{r.status.active}`, Restarts: `{r.status.restarts}`"]

    if r.issues:
        issues_txt = ", ".join(f"`{i.category}`" for i in r.issues)
        details.append(f"Issues detected: {issues_txt}")

    if r.samples:
        samples = "\n".join(f"  • `{ln[:160]}`" for ln in r.samples[:3])
        details.append("Log samples:\n" + samples)

    body = "\n".join(details)
    return f"{head}\n{body}"

def render_digest(d: DigestSummary) -> str:
    lines = [f"🖥️ *System Status Digest* (overall: {d.overall} {_badge(d.overall)})", ""]
    
    ordered_reports: Iterable[UnitReport] = sorted(d.reports, key=lambda x: {"FAIL": 0, "WARN": 1, "OK": 2}[x.level])
    
    for r in ordered_reports:
        lines.append(_format_report(r))
        lines.append("")
        
    return "\n".join(lines).strip()