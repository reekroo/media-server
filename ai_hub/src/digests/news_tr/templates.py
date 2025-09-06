def render_turkish_news_digest(section: str, llm_summary: str) -> str:
    return f"🇹🇷 Turkish News Digest ({section.capitalize()})\n\n{llm_summary.strip()}"