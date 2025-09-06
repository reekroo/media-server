from typing import Any
from .agents.base import Agent
from ..topics.base import TopicHandler

class Orchestrator:
    def __init__(self, agent: Agent, topics: dict[str, TopicHandler]):
        self.agent = agent
        self.topics = topics

    async def run(self, topic: str, payload: Any) -> Any:
        handler = self.topics[topic]
        prompt = handler.build_prompt(payload)
        text = await self.agent.generate(prompt)
        return handler.postprocess(text)
