from typing import List
from functions.sys.models import DigestSummary, UnitReport

def _badge(level: str) -> str:
    return {"OK": "✅", "WARN": "⚠️", "FAIL": "🛑"}.get(level, "❔")

def _format_warning(r: UnitReport) -> str:
    icon = _badge(r.level)
    parts = [f"{icon} *{r.unit}* — `{r.status.active}` (restarts: {r.status.restarts})"]

    if r.issues:
        issues_txt = ", ".join(f"`{i.category}`" for i in r.issues)
        parts.append(f"Issues: {issues_txt}")

    if r.samples:
        samples = "\n".join(f"  • `{ln[:160]}`" for ln in r.samples[:2])
        parts.append("Logs:\n" + samples)

    return "\n".join(parts)

def _format_ok(r: UnitReport) -> str:
    restarts_info = f" (restarts: {r.status.restarts})" if r.status.restarts > 0 else ""
    return f"• `{r.unit}{restarts_info}`"

def render_digest(d: DigestSummary) -> str:
    problem_reports: List[UnitReport] = []
    ok_reports: List[UnitReport] = []

    for r in d.reports:
        if r.level in ("FAIL", "WARN"):
            problem_reports.append(r)
        else:
            ok_reports.append(r)

    problem_reports.sort(key=lambda x: {"FAIL": 0, "WARN": 1}[x.level])

    lines: List[str] = []
    lines.append(
        f"🖥️ *System Status Digest*\n"
        f"Overall: {_badge(d.overall)} {d.overall} "
        f"({len(problem_reports)} issues, {len(ok_reports)} healthy)"
    )

    if problem_reports:
        lines.append("")
        lines.append(f"🚨 *Warnings ({len(problem_reports)}):*")
        lines.append("")
        for r in problem_reports:
            lines.append(_format_warning(r))
            lines.append("")

    if ok_reports:
        lines.append("")
        lines.append(f"✅ *Healthy ({len(ok_reports)}):*")
        lines.append("")
        for r in ok_reports:
            lines.append(_format_ok(r))
        lines.append("")

    lines.append(
        f"📊 Summary: {len(problem_reports)} need attention, {len(ok_reports)} healthy.\n"
        f"💡 Tip: Use `/why <service>` to get incident details."
    )

    return "\n".join(lines).strip()
