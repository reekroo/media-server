from typing import Iterable, List

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
    lines = [f"🖥️ *System Status Digest* (overall: {d.overall} {_badge(d.overall)})"]

    problem_reports: List[UnitReport] = []
    ok_reports: List[UnitReport] = []
    for r in d.reports:
        if r.level in ("FAIL", "WARN"):
            problem_reports.append(r)
        else:
            ok_reports.append(r)

    problem_reports.sort(key=lambda x: {"FAIL": 0, "WARN": 1}[x.level])

    if problem_reports:
        lines.extend(["", "--- WARNINGS ---", ""])
        for r in problem_reports:
            lines.append(_format_report(r))
            lines.append("")

    if ok_reports:
        lines.extend(["", f"--- ALL GOOD ({len(ok_reports)}) ---", ""])
        
        ok_lines: List[str] = []
        for r in ok_reports:
            restarts_info = f" (restarts: {r.status.restarts})" if r.status.restarts > 0 else ""
            ok_lines.append(f"`{r.unit}{restarts_info}`")
            
        lines.append(_badge("OK") + " " + ", ".join(ok_lines))
        
    return "\n".join(lines).strip()