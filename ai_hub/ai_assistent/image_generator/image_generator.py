from __future__ import annotations
from typing import Protocol, TYPE_CHECKING

from .vertex_client import get_generation_failure_reason, extract_image_bytes_from_part

if TYPE_CHECKING:
    from ..agents.base import Agent
    from vertexai.generative_models import GenerativeModel

class ImageGenerationError(Exception):
    pass

class ImageGenerator(Protocol):
    async def generate_from_prompt(self, user_prompt: str) -> bytes: ...
    async def generate_from_summary(self, text_summary: str) -> bytes: ...

_SUMMARY_REWRITE_PROMPT_INSTRUCTION = (
    "Rewrite the following into a concise English image prompt (one sentence). "
    "Keep it family-friendly and concrete:\n\n"
    "{text}\n\n"
    "Return ONLY the prompt."
)
_DEFAULT_ABSTRACT_PROMPT = "abstract minimalistic illustration"

class GeminiSdkImageGenerator:
    def __init__(self, agent: Agent, model: "GenerativeModel"):
        self._agent = agent
        self._model = model

    async def generate_from_prompt(self, user_prompt: str) -> bytes:
        prompt = (user_prompt or "").strip()
        if not prompt:
            raise ValueError("Image prompt cannot be empty.")

        try:
            response = await self._model.generate_content_async(prompt)
        except Exception as e:
            raise ImageGenerationError(f"Vertex AI API call failed: {e}") from e

        if not response.candidates or not response.candidates[0].content.parts:
            reason = get_generation_failure_reason(response)
            raise ImageGenerationError(f"Vertex AI returned no image. Reason: {reason}")
        
        try:
            image_part = response.candidates[0].content.parts[0]
            return extract_image_bytes_from_part(image_part)
        except (ValueError, IndexError) as e:
            raise ImageGenerationError("Failed to extract image data from API response.") from e

    async def generate_from_summary(self, text_summary: str) -> bytes:
        prompt = await self._summary_to_prompt(text_summary)
        return await self.generate_from_prompt(prompt)

    async def _summary_to_prompt(self, text_summary: str) -> str:
        text = (text_summary or "").strip()
        if not text:
            return _DEFAULT_ABSTRACT_PROMPT
        
        try:
            return await self._agent.generate(
                _SUMMARY_REWRITE_PROMPT_INSTRUCTION.format(text=text)
            )
        except Exception:
            return text