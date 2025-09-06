from __future__ import annotations
import asyncio
from src.core.settings import Settings
from src.core.agents.factory import agent_factory
from src.core.router import Orchestrator
from src.topics.weather import WeatherSummary

def _orch() -> Orchestrator:
    s = Settings()
    agent = agent_factory(api_key=s.GEMINI_API_KEY)
    topics = {"weather.summary": WeatherSummary()}
    return Orchestrator(agent, topics)

def weather_summary(payload: dict) -> str:
    orch = _orch()
    async def _run():
        return await orch.run("weather.summary", payload or {})
    return asyncio.run(_run())
