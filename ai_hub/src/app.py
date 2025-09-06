from __future__ import annotations
from pathlib import Path
import logging
import aiohttp

# --- Core Services ---
# Импортируем наш новый, единый класс Settings
from .core.settings import Settings
from .core.agents.factory import agent_factory
from .core.router import Orchestrator

# --- Topics ---
from .topics.weather import WeatherSummary
from .topics.quakes import QuakesAssessment
from .topics.movies import MoviesRecommend
from .topics.news import NewsDigestTopic
from .topics.gaming import GamingDigestTopic
from .topics.clarify import ClarifyIncident

# --- Digest Builders & Collectors ---
from .digests.brief.composer import DailyBriefComposer
from .digests.media.collector import NewTitlesCollector
from .digests.media.recommender import MediaRecommender
from .digests.media.templates import render_media_digest
from .digests.sys.build import SystemDigestBuilder
from .digests.news.collector import NewsFeedCollector
from .digests.news.templates import render_news_digest
from .digests.gaming.collector import FeedCollector as GamingFeedCollector
from .digests.gaming.templates import render_gaming_digest

# --- Channels ---
from .channels.telegram_send.telegram_send import TelegramClient
from .channels.console.console import send_to_console

class App:
    """The core application, containing all services and business logic."""

    def __init__(self):
        logging.info("Initializing application core...")
        # Создаем экземпляр Settings. Вся магия загрузки конфигов происходит внутри него.
        self.settings = Settings()
        
        # --- Инициализируем сервисы, используя готовый объект settings ---
        self.agent = agent_factory(self.settings)
        self.orchestrator = self._build_orchestrator()
        self.http_session = aiohttp.ClientSession()
        
        if self.settings.TELEGRAM_BOT_TOKEN:
            self.telegram_client = TelegramClient(self.settings.TELEGRAM_BOT_TOKEN)
        else:
            self.telegram_client = None
        logging.info("Application core initialized.")

    def _build_orchestrator(self) -> Orchestrator:
        """Собирает оркестратор со всеми доступными топиками."""
        topics = {
            "weather.summary": WeatherSummary(),
            "quakes.assess": QuakesAssessment(),
            "movies.recommend": MoviesRecommend(),
            "news.digest": NewsDigestTopic(),
            "gaming.digest": GamingDigestTopic(),
            "clarify.incident": ClarifyIncident(),
        }
        return Orchestrator(self.agent, topics)
        
    async def close_resources(self):
        """Корректно закрывает сетевые соединения."""
        await self.http_session.close()

    async def send_notification(self, message: str, send_to: str = "default"):
        """Отправляет уведомление в настроенный канал."""
        if (send_to == "telegram" or send_to == "default") and self.telegram_client and self.settings.TELEGRAM_CHAT_ID:
            await self.telegram_client.send_text(self.settings.TELEGRAM_CHAT_ID, message)
        else:
            send_to_console(message)

    # --- Бизнес-логика для каждого дайджеста ---

    async def run_daily_brief(self) -> str:
        cfg = self.settings.daily
        if not cfg:
            return "Daily brief config not found or invalid."
        
        composer = DailyBriefComposer(self.orchestrator)
        # Пути к файлам weather/quakes берутся из settings, которые могли быть переопределены в daily.toml
        # (Логику обработки этого можно добавить в Settings, если требуется)
        return await composer.compose(
            weather_json=Path("/run/monitors/weather/latest.json"), # Пример, лучше брать из settings
            quakes_json=Path("/run/monitors/earthquakes/last7d.json"), # Пример
            include_quakes=cfg.include_quakes
        )

    async def run_media_digest(self) -> str:
        cfg = self.settings.media
        if not (cfg and cfg.enabled):
            return "Media digest is disabled in config."

        collector = NewTitlesCollector(
            state_path=cfg.state_path,
            include_ext=cfg.include_ext,
            max_depth=cfg.max_depth
        )
        new_titles = await collector.collect(root=cfg.root)
        
        recommender = MediaRecommender(self.orchestrator)
        rec_text = await recommender.build(
            root=cfg.root,
            prefs=cfg.recommender.model_dump(),
            cap=600 # Это значение тоже можно вынести в конфиг
        )
        return render_media_digest(new_titles=new_titles, recommend_text=rec_text)

    async def run_sys_digest(self) -> str:
        cfg = self.settings.sys
        if not (cfg and cfg.enabled):
            return "System digest is disabled in config."
        
        builder = SystemDigestBuilder(
            config=cfg.model_dump(),
            incidents_dir=self.settings.STATE_DIR / "incidents",
            state_path=self.settings.STATE_DIR / "sys_digest.json"
        )
        _, msg = await builder.build()
        return msg
        
    async def run_news_digest(self) -> list[str]:
        cfg = self.settings.news
        if not (cfg and cfg.enabled):
            return []

        collector = NewsFeedCollector(self.http_session)
        messages = []
        for section, urls in cfg.feeds.items():
            items = await collector.collect(urls, max_items=cfg.max_items)
            if not items: continue
            
            summary = await self.orchestrator.run("news.digest", {"items": items, "section": section})
            messages.append(render_news_digest(section, summary))
        return messages

    async def run_gaming_digest(self) -> list[str]:
        cfg = self.settings.gaming
        if not (cfg and cfg.enabled):
            return []

        collector = GamingFeedCollector(self.http_session)
        all_items = []
        for _, urls in cfg.feeds.items():
            all_items.extend(await collector.collect(urls))
            
        if not all_items: return []
        
        summary = await self.orchestrator.run("gaming.digest", {"items": all_items[:cfg.max_items]})
        return [render_gaming_digest(summary)]