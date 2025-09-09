from __future__ import annotations
from typing import List

def _render_new_titles_section(new_titles: List[str]) -> str:
    if not new_titles:
        return "📥 New in library: none"
    
    header = f"📥 New in library ({len(new_titles)}):"
    
    titles_to_show = [f"• {title}" for title in new_titles[:20]]
    
    if len(new_titles) > 20:
        titles_to_show.append(f"… +{len(new_titles) - 20} more")
        
    return f"{header}\n" + "\n".join(titles_to_show)

def render_media_digest(
    *, new_titles: List[str], recommend_text: str, soon_text: str | None = None
) -> str:
    parts = [
        _render_new_titles_section(new_titles),
        "\n🎯 Suggestions:\n" + recommend_text.strip(),
    ]
    
    if soon_text:
        parts.append("\n🎬 Coming soon:\n" + soon_text.strip())
        
    return "\n".join(parts).strip()