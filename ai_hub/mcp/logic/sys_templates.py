# mcp/logic/sys_templates.py

from typing import Iterable
from  ...functions.sys.model import DigestSummary, UnitReport

def _badge(level: str) -> str:
    """Возвращает emoji-значок для уровня состояния."""
    return {"OK": "✅", "WARN": "⚠️", "FAIL": "🛑"}.get(level, "❔")

def _format_report(r: UnitReport) -> str:
    """Форматирует отчет по одному systemd-юниту."""
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
    """Собирает полный текстовый дайджест из всех отчетов."""
    lines = [f"🖥️ *System Status Digest* (overall: {d.overall} {_badge(d.overall)})", ""]
    
    # Сортируем: сначала проблемы, потом все остальное
    ordered_reports: Iterable[UnitReport] = sorted(d.reports, key=lambda x: {"FAIL": 0, "WARN": 1, "OK": 2}[x.level])
    
    for r in ordered_reports:
        lines.append(_format_report(r))
        lines.append("") # Пустая строка для разделения
        
    return "\n".join(lines).strip()