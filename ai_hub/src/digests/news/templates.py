from __future__ import annotations

def render_news_digest(section: str, summary_text: str) -> str:
    return f"🗞️ {section.capitalize()} news\n{summary_text.strip()}"