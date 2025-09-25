import google.generativeai as genai

from .gemini_agent import GeminiSDKAgent
from .base import Agent
from core.settings import Settings

def agent_factory(settings: Settings) -> Agent:
    api_key = settings.GEMINI_API_KEY
    model = settings.GEMINI_MODEL

    if api_key:
        genai.configure(api_key=api_key)
    else:
        raise ValueError("GEMINI_API_KEY is not set.")
    
    return GeminiSDKAgent(model=model)