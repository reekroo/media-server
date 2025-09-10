import pkgutil
import inspect
from pathlib import Path
from importlib import import_module
from typing import Any, Dict

from .agents.base import Agent
from .topics.base import TopicHandler

class DigestService:
    """
    Оркестратор "мозга". Автоматически находит, регистрирует и запускает
    все доступные топики (TopicHandler).
    """
    def __init__(self, agent: Agent):
        self.agent = agent
        self.topics: Dict[str, TopicHandler] = self._discover_topics()
        print(f"✅ DigestService initialized. Registered topics: {', '.join(self.topics.keys())}")

    def _discover_topics(self) -> Dict[str, TopicHandler]:
        """Сканирует директорию topics/ и регистрирует все обработчики."""
        topics = {}
        # Путь к директории с топиками относительно этого файла
        topics_dir = Path(__file__).parent / "topics"
        
        for module_info in pkgutil.iter_modules([str(topics_dir)]):
            module_name = module_info.name
            if module_name == "base":  # Пропускаем базовый класс
                continue
            
            module = import_module(f".topics.{module_name}", package="ai_assistent")
            for _, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, TopicHandler) and obj is not TopicHandler:
                    # Регистрируем топик по имени файла (clarify.py -> 'clarify')
                    topic_name = module_name
                    topics[topic_name] = obj()
                    print(f"  -> Discovered topic '{topic_name}' from {obj.__name__}")
        return topics

    async def digest(self, kind: str, params: Dict[str, Any]) -> str:
        """Выполняет пайплайн для указанного топика."""
        handler = self.topics.get(kind)
        if not handler:
            raise KeyError(f"Unknown topic kind '{kind}'. Available: {', '.join(self.topics.keys())}")

        prompt = handler.build_prompt(params)
        text = await self.agent.generate(prompt)
        return handler.postprocess(text)