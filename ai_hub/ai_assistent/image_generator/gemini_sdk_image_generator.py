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

    async def generate_from_prompt(self, user_prompt: str) -> bytes:
        print(f"Generating image with direct prompt: {user_prompt}")
        return await self._generate_image_from_final_prompt(user_prompt)

    async def generate_from_summary(self, text_summary: str) -> bytes:
        prompt_for_image_prompt = (
            f"Create a concise, artistic, and visually compelling image prompt "
            f"based on this news summary: '{text_summary[:500]}'. "
            "The prompt should be in English, a maximum of 20 words, suitable for an AI image generator."
        )
        image_prompt = await self._agent.generate(prompt_for_image_prompt)
        image_prompt = image_prompt.strip().strip('"')

        print(f"Generating image for summary with generated prompt: {image_prompt}")
        return await self._generate_image_from_final_prompt(image_prompt)

    async def _generate_image_from_final_prompt(self, final_prompt: str) -> bytes:
        try:
            images = self.model.generate_images(
                prompt=final_prompt,
                number_of_images=1
            )
            if images and images[0]._image_bytes:
                return images[0]._image_bytes
            else:
                raise ValueError("API returned no image data.")
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