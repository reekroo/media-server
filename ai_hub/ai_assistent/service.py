import pkgutil
import inspect
from pathlib import Path
from importlib import import_module
from typing import Any, Dict

from core.settings import Settings
from .agents.base import Agent
from .topics.base import TopicHandler
from .translation.gemini_sdk_translator import SdkTranslator

class DigestService:
    def __init__(self, agent: Agent, settings: Settings):
        self.agent = agent
        self.settings = settings
        self.default_lang = settings.DEFAULT_LANG
        self.topics: Dict[str, TopicHandler] = self._discover_topics()
        self.translator = SdkTranslator(agent)
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