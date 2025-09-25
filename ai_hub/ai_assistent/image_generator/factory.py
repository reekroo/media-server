import vertexai
from core.settings import Settings
from ..agents.base import Agent

from .legacy_image_generator import LegacyImageGenerator
from .image_generator import GeminiSdkImageGenerator as ModernImageGenerator

def image_generator_factory(settings: Settings, agent: Agent):
    vertexai.init(project=settings.GCP_PROJECT_ID, location=settings.GCP_LOCATION)

    if settings.USE_LEGACY_IMAGE_GENERATOR:
        print("✅ Using LEGACY image generator")
        from vertexai.preview.vision_models import ImageGenerationModel
        
        model = ImageGenerationModel.from_pretrained(settings.VERTEX_LEGACY_IMAGE_MODEL)
        return LegacyImageGenerator(agent=agent, model=model)
    else:
        print("✅ Using MODERN image generator")
        from vertexai.generative_models import GenerativeModel

        model = GenerativeModel(settings.VERTEX_IMAGE_MODEL)
        return ModernImageGenerator(agent=agent, model=model)