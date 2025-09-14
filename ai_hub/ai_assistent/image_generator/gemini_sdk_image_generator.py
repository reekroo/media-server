from __future__ import annotations
from typing import Optional, Protocol
from .utils import ensure_vertex_model, extract_image_bytes, extract_generation_reasons

from ..agents.base import Agent

class ImageGenerator(Protocol):
    async def generate_from_prompt(self, user_prompt: str) -> bytes: ...
    async def generate_from_summary(self, text_summary: str) -> bytes: ...

class GeminiSdkImageGenerator:
    def __init__(self, agent: Agent, project_id: Optional[str], location: Optional[str]):
        self._agent = agent
        self._project_id = project_id
        self._location = location
        self._model = None

    async def generate_from_prompt(self, user_prompt: str) -> bytes:
        prompt = (user_prompt or "").strip()
        if not prompt:
            raise ValueError("Empty image prompt")

        model = self._get_model()
        try:
            result = model.generate_images(
                prompt=prompt,
                number_of_images=1,
                aspect_ratio="1:1",
            )
        except Exception as e:
            raise RuntimeError(f"Vertex image generation failed: {e}") from e

        images = getattr(result, "images", None)
        if not images:
            reasons = extract_generation_reasons(result) or "unknown reason"
            raise RuntimeError(f"Vertex returned no images: {reasons}")

        img0 = images[0]
        data = extract_image_bytes(img0)
        if not data:
            raise RuntimeError("Unsupported image object returned by Vertex SDK")

        return data

    async def generate_from_summary(self, text_summary: str) -> bytes:
        prompt = await self._summary_to_prompt(text_summary)
        return await self.generate_from_prompt(prompt)

    def _get_model(self):
        if self._model is None:
            self._model = ensure_vertex_model(self._project_id, self._location)
        return self._model

    async def _summary_to_prompt(self, text_summary: str) -> str:
        text = (text_summary or "").strip()
        if not text:
            return "abstract minimalistic illustration"
        try:
            return await self._agent.generate(
                "Rewrite the following into a concise English image prompt (one sentence). "
                "Keep it family-friendly and concrete:\n\n"
                f"{text}\n\n"
                "Return ONLY the prompt."
            )
        except Exception:
            return text
