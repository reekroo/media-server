from typing import Protocol

import vertexai
from vertexai.preview.vision_models import ImageGenerationModel

from ..agents.base import Agent

class ImageGenerator(Protocol):
    async def generate(self, text_summary: str) -> bytes: ...

class GeminiSdkImageGenerator(ImageGenerator):
    def __init__(self, agent: Agent, project_id: str, location: str):
        self._agent = agent
        vertexai.init(project=project_id, location=location)
        self.model = ImageGenerationModel.from_pretrained("imagegeneration@005")

    async def generate(self, text_summary: str) -> bytes:
        prompt_for_image_prompt = (
            f"based on this news summary: '{text_summary[:500]}'. "
            "Prompt should be in English, max 20 words."
        )
        image_prompt = await self._agent.generate(prompt_for_image_prompt)
        image_prompt = image_prompt.strip()

        print(f"Generating real image with prompt: {image_prompt}")

        try:
            images = self.model.generate_images(
                prompt=image_prompt,
                number_of_images=1
            )
            return images[0]._image_bytes
        except Exception as e:
            print(f"Failed to generate image via Vertex AI: {e}. Falling back to placeholder.")
            return await self._create_placeholder_image(f"API ERROR:\n{e}")
    
    async def _create_placeholder_image(self, text: str) -> bytes:
        from PIL import Image, ImageDraw, ImageFont
        import io
        img = Image.new('RGB', (1024, 1024), color = (75, 25, 25))
        d = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except IOError:
            font = ImageFont.load_default()
        d.text((50,50), "IMAGE GENERATION FAILED\n\n" + text, fill=(255,255,255), font=font)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()