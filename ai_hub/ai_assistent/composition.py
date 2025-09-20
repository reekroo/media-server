from core.settings import Settings
from .agents.factory import agent_factory
from .summarizer.summarizer import SdkSummarizer
from .translation.translator import SdkTranslator
from .image_generator.image_generator import GeminiSdkImageGenerator
from .image_generator.vertex_client import create_vertex_ai_model
from .service import DigestService

def create_digest_service(settings: Settings) -> DigestService:
    text_agent = agent_factory(settings)
    vertex_image_model = create_vertex_ai_model(settings)

    summarizer = SdkSummarizer(text_agent)
    translator = SdkTranslator(text_agent)
    image_generator = GeminiSdkImageGenerator(
        agent=text_agent,
        model=vertex_image_model
    )

    return DigestService(
        agent=text_agent,
        settings=settings,
        summarizer=summarizer,
        translator=translator,
        image_generator=image_generator
    )