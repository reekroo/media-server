from __future__ import annotations
import random
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
        
        safe_fallbacks = [
            "abstract minimalistic illustration, clean background",
            "serene landscape with geometric shapes, digital art",
            "a calm ocean with a single boat at sunset, vector art",
            "futuristic city skyline at night, cinematic lighting",
            "detailed macro shot of a water droplet on a leaf, photorealistic"
        ]

        if not text:
            return random.choice(safe_fallbacks)

        instructions = f"""
You are an expert in transforming news summaries into safe, neutral, and visually compelling image prompts. Your task is to rewrite the given summary into a single, concrete English sentence suitable for an image generation model.

**Rules:**
1.  **Be Visual and Concrete:** Do not use abstract concepts. Describe a specific scene, characters, or objects. Create a visual metaphor if the topic is complex.
2.  **Strictly Safe-for-Work (SFW):** AVOID any words related to violence, weapons, blood, death, politics, religion, or any sensitive conflict.
3.  **Add a Style:** End the prompt with an appropriate artistic style (e.g., "digital art", "photorealistic", "vector illustration", "cinematic lighting").
4.  **Output Format:** Return ONLY the final image prompt and nothing else.

**Examples:**

Original summary: "Leaders of two countries held tense negotiations over a trade dispute, ending without an agreement."
Your prompt: Two businesspersons sitting opposite each other at a chess table with a single pawn in the middle, dramatic lighting, digital art.

Original summary: "A new study reveals alarming rates of deforestation in the Amazon rainforest due to illegal logging."
Your prompt: A vibrant, detailed illustration of a half-lush, half-barren forest with a glowing line separating the two halves, top-down view.

---
**Now, transform the following summary:**

Original summary: {text}
"""
        try:
            generated_prompt = await self._agent.generate(instructions)
            
            if generated_prompt and generated_prompt.strip():
                return generated_prompt.strip()
            else:
                return random.choice(safe_fallbacks)

        except Exception as e:
            print(f"Error during prompt generation, using fallback: {e}") 
            return random.choice(safe_fallbacks)