from core.settings import Settings
from .agents.factory import agent_factory
from .summarizer.summarizer import SdkSummarizer
from .translation.translator import SdkTranslator
from .image_generator.image_generator import GeminiSdkImageGenerator
from .image_generator.vertex_client import create_vertex_ai_model
from .service import DigestService
from .image_generator.factory import image_generator_factory

def create_digest_service(settings: Settings) -> DigestService:
    text_agent = agent_factory(settings)
    vertex_image_model = create_vertex_ai_model(settings)

    summarizer = SdkSummarizer(text_agent)
    translator = SdkTranslator(text_agent)
    image_generator = image_generator_factory(settings, agent=text_agent)

    return DigestService(
        agent=text_agent,
        settings=settings,
        summarizer=summarizer,
        translator=translator,
        image_generator=image_generator
    )