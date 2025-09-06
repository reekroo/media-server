import google.generativeai as genai
from .base import Agent

class GeminiSDKAgent(Agent):
    name = "gemini-sdk"

    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        genai.configure(api_key=api_key)
        self._model = genai.GenerativeModel(model)

    async def generate(self, prompt: str) -> str:
        resp = self._model.generate_content(prompt)
        return (resp.text or "").strip()

    async def stream(self, prompt: str):
        stream = self._model.generate_content(prompt, stream=True)
        acc = ""
        for ev in stream:
            if getattr(ev, "text", None):
                acc += ev.text
                yield acc
