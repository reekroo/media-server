import os
from .gemini_sdk import GeminiSDKAgent

def agent_factory(api_key: str, model: str | None = None):
    model = model or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    
    return GeminiSDKAgent(api_key=api_key, model=model)