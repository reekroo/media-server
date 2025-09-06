from __future__ import annotations

def render_media_digest(*, new_titles: list[str], recommend_text: str, soon_text: str | None = None) -> str:
    parts = []
    if new_titles:
        parts.append("📥 New in library (" + str(len(new_titles)) + "):\n" + "\n".join(f"• {t}" for t in new_titles[:20]) + (f"\n… +{len(new_titles)-20} more" if len(new_titles) > 20 else ""))
    else:
        parts.append("📥 New in library: none")
    parts.append("\n🎯 Suggestions:\n" + recommend_text.strip())
    if soon_text:
        parts.append("\n🎬 Coming soon:\n" + soon_text.strip())
    return "\n".join(parts).strip()
