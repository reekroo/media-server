import textwrap
from .base import TopicHandler
from .utils import format_items_for_prompt, create_summary_instruction

class GamingDigestTopic(TopicHandler):
    def build_prompt(self, payload: dict) -> str:
        items = payload.get("items", [])[:30]
        count = payload.get("count")
        
        block = format_items_for_prompt(items)
        summary_instruction = create_summary_instruction(
            count, 
            default="Create 5–10 concise bullets for core updates"
        )
        
        return textwrap.dedent(f"""
            You are a gaming news curator. {summary_instruction} (releases, patches, delays, trailers).
          
            IMPORTANT, OUTPUT FORMAT (STRICT):
            - Use simple Markdown ONLY.
            - Use asterisks for bold section titles (*Title*).
            - Put ONE blank line between items.
                               
            Keep it actionable (dates/platforms). Avoid hype.
            
            Items:
                {block}
        """).strip()