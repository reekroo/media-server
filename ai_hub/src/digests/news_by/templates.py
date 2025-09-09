def render_belarus_news_digest(section: str, llm_summary: str) -> str:
    return f"🇧🇾 Belarus News Digest ({section.capitalize()})\n\n{llm_summary.strip()}"