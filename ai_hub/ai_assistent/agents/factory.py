from .gemini_sdk import GeminiSDKAgent
from .base import Agent
from core.settings import Settings

def agent_factory(settings: Settings) -> Agent:
    api_key = settings.GEMINI_API_KEY
    model = settings.GEMINI_MODEL
    
    return GeminiSDKAgent(api_key=api_key, model=model)