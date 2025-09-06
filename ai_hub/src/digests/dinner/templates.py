def render_dinner_digest(llm_summary: str) -> str:
    return f"👩‍🍳 What's for Dinner?\n(A few ideas for tonight)\n\n{llm_summary.strip()}"