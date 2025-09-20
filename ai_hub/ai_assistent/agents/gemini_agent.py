import google.generativeai as genai

from .base import Agent

class GeminiSDKAgent(Agent):
    name = "gemini-sdk"
    DEFAULT_MODEL = "gemini-2.5-flash" 

    def __init__(self, model: str | None = None):
        model_name = model or self.DEFAULT_MODEL
        self._model = genai.GenerativeModel(model_name)

    async def generate(self, prompt: str) -> str:
        resp = await self._model.generate_content_async(prompt)

        if not resp.text:
             return f"Generation failed: {resp.prompt_feedback}"
        return resp.text.strip()

    async def stream(self, prompt: str):
        stream = await self._model.generate_content_async(prompt, stream=True)
        acc = ""
        async for ev in stream:
            if getattr(ev, "text", None):
                acc += ev.text
                yield acc