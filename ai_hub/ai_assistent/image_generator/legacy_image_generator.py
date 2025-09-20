from __future__ import annotations
from typing import TYPE_CHECKING
from ..agents.base import Agent

if TYPE_CHECKING:
    from vertexai.preview.vision_models import ImageGenerationModel

class LegacyImageGenerator:
    def __init__(self, agent: Agent, model: "ImageGenerationModel"):
        self._agent = agent
        self._model = model

    async def generate_from_prompt(self, user_prompt: str) -> bytes:
        prompt = (user_prompt or "").strip()
        if not prompt:
            raise ValueError("Image prompt cannot be empty.")

        try:
            result = self._model.generate_images(prompt=prompt, number_of_images=1)
            image = result.images[0]
            return image._image_bytes
        except Exception as e:
            raise RuntimeError(f"Legacy Vertex image generation failed: {e}") from e

    async def generate_from_summary(self, text_summary: str) -> bytes:
        prompt = await self._summary_to_prompt(text_summary)
        return await self.generate_from_prompt(prompt)

    async def _summary_to_prompt(self, text_summary: str) -> str:
        text = (text_summary or "").strip()
        if not text: return "abstract minimalistic illustration"
        try:
            return await self._agent.generate(
                "Rewrite the following into a concise English image prompt...\n\n"
                f"{text}\n\n"
                "Return ONLY the prompt."
            )
        except Exception:
            return text