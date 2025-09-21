import pkgutil
import inspect
from pathlib import Path
from importlib import import_module
from typing import Any, Dict

from core.settings import Settings
from .topics.base import TopicHandler
from .agents.base import Agent

from .summarizer.base import Summarizer
from .translation.base import Translator
from .image_generator.image_generator import ImageGenerator

class DigestService:
    def __init__(
        self,
        agent: Agent,
        settings: Settings,
        summarizer: Summarizer,
        translator: Translator,
        image_generator: ImageGenerator,
    ):
        self.agent = agent
        self.settings = settings
        self.summarizer = summarizer
        self.translator = translator
        self.image_generator = image_generator
        
        self.default_lang = settings.DEFAULT_LANGUAGE
        self.topics: Dict[str, TopicHandler] = self._discover_topics()
        
        print(f"✅ DigestService initialized. Registered topics: {', '.join(self.topics.keys())}")

    def _discover_topics(self) -> Dict[str, TopicHandler]:
        topics = {}
        topics_dir = Path(__file__).parent / "topics"
        
        for module_info in pkgutil.iter_modules([str(topics_dir)]):
            module_name = module_info.name
            if module_name == "base": continue
            
            module = import_module(f".topics.{module_name}", package="ai_assistent")
            for _, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, TopicHandler) and obj is not TopicHandler:
                    topics[module_name] = obj()
                    print(f"☑️ Discovered topic '{module_name}' from {obj.__name__}")
        return topics

    async def digest(self, kind: str, params: Dict[str, Any]) -> str:
        handler = self.topics.get(kind)
        if not handler:
            raise KeyError(f"🟥 Unknown topic kind '{kind}'. Available: {', '.join(self.topics.keys())}")

        prompt = handler.build_prompt(params)
        text = await self.agent.generate(prompt)
        return handler.postprocess(text)
    
    async def translate(self, text: str, target_lang: str) -> str:
        if not text or not target_lang:
            return text
        return await self.translator.translate(text, target_lang)
    
    async def summarize(self, text: str, max_chars: int = 220) -> str:
        return await self.summarizer.summarize_for_image(text, max_chars=max_chars)

    async def generate_image_from_prompt(self, user_prompt: str) -> bytes:
        return await self.image_generator.generate_from_prompt(user_prompt)

    async def generate_image_from_summary(self, text_summary: str) -> bytes:
        return await self.image_generator.generate_from_summary(text_summary)