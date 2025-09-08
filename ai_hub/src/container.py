from __future__ import annotations
import logging
import aiohttp
import importlib
from pathlib import Path
from functools import partial
from dataclasses import dataclass

from .core.settings import Settings
from .core.agents.factory import agent_factory
from .core.agents.base import Agent
from .core.router import Orchestrator
from .core.dispatcher import DigestDispatcher
from .common.feed_collector import FeedCollector
from .channels.telegram_send.telegram_send import TelegramClient

from .topics.weather import WeatherSummary
from .topics.quakes import QuakesAssessment
from .topics.movies import MoviesRecommend
from .topics.news import NewsDigestTopic
from .topics.gaming import GamingDigestTopic
from .topics.clarify import ClarifyIncident
from .topics.logs import LogAnalysisTopic
from .topics.news_tr import TurkishNewsDigestTopic
from .topics.news_by import BelarusNewsDigestTopic
from .topics.entertainment import EntertainmentDigestTopic
from .topics.dinner import DinnerRecipeTopic

from .jobs import (
    daily_brief_job,
    dinner_job,
    entertainment_job,
    gaming_job,
    logs_job,
    media_job,
    news_job,
    news_tr_job,
    news_by_job,
    sys_job,
    weather_job,
    quakes_job
)

@dataclass
class Services:
    settings: Settings
    agent: Agent
    orchestrator: Orchestrator
    http_session: aiohttp.ClientSession
    feed_collector: FeedCollector
    dispatcher: DigestDispatcher
    telegram_client: TelegramClient | None

def build_services() -> Services:
    logging.info("Building application services...")
    
    settings = Settings()
    agent = agent_factory(settings)
    orchestrator = _build_orchestrator(agent)
    
    http_session = aiohttp.ClientSession()
    feed_collector = FeedCollector(http_session)
    dispatcher = DigestDispatcher()
    
    telegram_client = TelegramClient(settings.TELEGRAM_BOT_TOKEN) if settings.TELEGRAM_BOT_TOKEN else None

    services = Services(
        settings=settings, 
        agent=agent, 
        orchestrator=orchestrator,
        http_session=http_session, 
        feed_collector=feed_collector,
        dispatcher=dispatcher, 
        telegram_client=telegram_client
    )

    _register_jobs(dispatcher, services)

    logging.info("All services and jobs are built and registered.")
    return services

def _build_orchestrator(agent: Agent) -> Orchestrator:
    topics = {
        "dinner.suggest": DinnerRecipeTopic(),
        "weather.summary": WeatherSummary(), 
        "quakes.summary": QuakesAssessment(),
        "movies.recommend": MoviesRecommend(), 
        "entertainment.digest": EntertainmentDigestTopic(), 
        "news.digest": NewsDigestTopic(),
        "news.tr.digest": TurkishNewsDigestTopic(),
        "news.by.digest": BelarusNewsDigestTopic(),
        "gaming.digest": GamingDigestTopic(), 
        "logs.analyze": LogAnalysisTopic(), 
        "clarify.incident": ClarifyIncident(),
    }
    return Orchestrator(agent, topics)

def _register_jobs(dispatcher: DigestDispatcher, services: Services):
    logging.info("Registering jobs manually...")

    job_map = {
        "daily_brief": daily_brief_job.run,
        "dinner": dinner_job.run,
        "weather": weather_job.run,
        "quakes": quakes_job.run,
        "media": media_job.run,
        "entertainment": entertainment_job.run,
        "news": news_job.run,
        "news_tr": news_tr_job.run,
        "news_by": news_by_job.run,
        "gaming": gaming_job.run,
        "logs": logs_job.run,
        "sys": sys_job.run,
    }

    for name, func in job_map.items():
        bound_job = partial(func)
        dispatcher.register(name, bound_job)
    
    return dispatcher
