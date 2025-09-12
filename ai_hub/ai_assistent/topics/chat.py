import textwrap

from .base import TopicHandler

class ChatTopic(TopicHandler):
    def build_prompt(self, payload: dict) -> str:
        history = payload.get("history", [])
        
        history_lines = []
        for turn in history:
            history_lines.append(f"User: {turn['user']}")
            history_lines.append(f"Assistant: {turn['assistant']}")
            
        history_block = "\n".join(history_lines)
        
        return textwrap.dedent(f"""
            You are a helpful and friendly assistant. Continue the conversation based on the history.

            Conversation History:
                {history_block}
        """).strip()

    def postprocess(self, llm_text: str) -> str:
        return (llm_text or "").strip()