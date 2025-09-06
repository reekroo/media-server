from __future__ import annotations
from pathlib import Path
import logging
import aiohttp
import tomllib

from .core.settings import Settings
from .core.agents.factory import agent_factory
from .core.router import Orchestrator

from .topics.weather import WeatherSummary
from .topics.quakes import QuakesAssessment
from .topics.movies import MoviesRecommend
from .topics.news import NewsDigestTopic
from .topics.gaming import GamingDigestTopic
from .topics.clarify import ClarifyIncident

from .digests.brief.composer import DailyBriefComposer
from .digests.media.collector import NewTitlesCollector
from .digests.media.recommender import MediaRecommender
from .digests.media.templates import render_media_digest
from .digests.sys.build import SystemDigestBuilder
from .digests.news.templates import render_news_digest
from .digests.gaming.templates import render_gaming_digest

from .channels.telegram_send.telegram_send import TelegramClient
from .channels.console.console import send_to_console

from .common.feed_collector import FeedCollector

class App:
    def __init__(self):
        logging.info("Initializing application core...")
        self.settings = Settings()
        
        self.agent = agent_factory(self.settings)
        self.orchestrator = self._build_orchestrator()
        self.http_session = aiohttp.ClientSession()
        self.feed_collector = FeedCollector(self.http_session)
        
        if self.settings.TELEGRAM_BOT_TOKEN:
            self.telegram_client = TelegramClient(self.settings.TELEGRAM_BOT_TOKEN)
        else:
            self.telegram_client = None
        logging.info("Application core initialized.")

    def _build_orchestrator(self) -> Orchestrator:
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
        await self.http_session.close()

    async def send_notification(self, message: str, send_to: str = "default"):
        if (send_to == "telegram" or send_to == "default") and self.telegram_client and self.settings.TELEGRAM_CHAT_ID:
            await self.telegram_client.send_text(self.settings.TELEGRAM_CHAT_ID, message)
        else:
            send_to_console(message)

    async def run_weather_summary(self, payload: dict | None = None) -> str:
        if not payload:
             weather_path = Path("/run/monitors/weather/latest.json")
             if not weather_path.exists(): return "Weather data file not found."
             payload = json.loads(weather_path.read_text("utf-8"))
        
        return await self.orchestrator.run("weather.summary", payload or {})

    async def run_daily_brief(self, config_path_override: str | None = None) -> str:
        cfg_path = Path(config_path_override) if config_path_override else self.settings.BASE_DIR / "configs" / "daily.toml"
        if not cfg_path.exists(): return "Daily brief config not found."
        cfg_data = tomllib.loads(cfg_path.read_text("utf-8")).get("brief", {})

        composer = DailyBriefComposer(self.orchestrator)
        weather_path = Path("/run/monitors/weather/latest.json")
        quakes_path = Path("/run/monitors/earthquakes/last7d.json")

        return await composer.compose(
            weather_json=weather_path,
            quakes_json=quakes_path,
            include_quakes=cfg_data.get("include_quakes", True)
        )

    async def run_media_digest(self, config_path_override: str | None = None) -> str:
        cfg_path = Path(config_path_override) if config_path_override else self.settings.BASE_DIR / "configs" / "media.toml"
        if not cfg_path.exists(): return "Media config not found."
        cfg = tomllib.loads(cfg_path.read_text("utf-8"))

        state_path = self.settings.BASE_DIR / Path(cfg.get("state_path", "state/media_index.json"))
        root_path = Path(cfg.get("root", "/media"))

        collector = NewTitlesCollector(
            state_path=state_path,
            include_ext=cfg.get("include_ext", []),
            max_depth=int(cfg.get("max_depth", 6))
        )
        new_titles = await collector.collect(root=root_path)
        
        recommender = MediaRecommender(self.orchestrator)
        rec_text = await recommender.build(
            root=root_path,
            prefs=cfg.get("recommender", {}),
            cap=int(cfg.get("cap", 600))
        )
        return render_media_digest(new_titles=new_titles, recommend_text=rec_text)

    async def run_sys_digest(self, config_path_override: str | None = None) -> str:
        config_path = Path(config_path_override) if config_path_override else self.settings.BASE_DIR / "configs" / "sys.toml"
        if not config_path.exists(): return "System digest config not found."
        
        builder = SystemDigestBuilder(
            config=tomllib.loads(config_path.read_text("utf-8")),
            incidents_dir=self.settings.STATE_DIR / "incidents",
            state_path=self.settings.STATE_DIR / "sys_digest.json"
        )
        _, msg = await builder.build()
        return msg
        
    async def run_news_digest(self, config_path_override: str | None = None, section: str | None = None) -> str:
        config_path = Path(config_path_override) if config_path_override else self.settings.BASE_DIR / "configs" / "news.toml"
        if not config_path.exists(): return "News config not found."
        cfg = tomllib.loads(config_path.read_text("utf-8"))
        if not cfg.get("enabled", False): return "News digest is disabled."
        
        feeds = cfg.get("feeds", {})
        if not feeds: return "No news feeds configured."

        key = section if section in feeds else next(iter(feeds.keys()), None)
        if not key: return "No news section available."

        urls = feeds[key]
        items = await self.feed_collector.collect(urls, max_items=int(cfg.get("max_items", 20)))
        if not items: return f"No items found for news section '{key}'."
            
        items_payload = [item.model_dump() for item in items]
        summary = await self.orchestrator.run("news.digest", {"items": items_payload, "section": key})
        return render_news_digest(key, summary)

    async def run_gaming_digest(self, config_path_override: str | None = None) -> str:
        config_path = Path(config_path_override) if config_path_override else self.settings.BASE_DIR / "configs" / "gaming.toml"
        if not config_path.exists(): return "Gaming config not found."
        cfg = tomllib.loads(config_path.read_text("utf-8"))
        if not cfg.get("enabled", False): return "Gaming digest is disabled."

        all_urls = [url for urls in cfg.get("feeds", {}).values() for url in urls]
        if not all_urls: return "No gaming feeds configured."
        
        all_items = await self.feed_collector.collect(all_urls)
        if not all_items: return "No items found for gaming feeds."
        
        items_payload = [item.model_dump() for item in all_items[:int(cfg.get("max_items", 20))]]
        summary = await self.orchestrator.run("gaming.digest", {"items": items_payload})
        return render_gaming_digest(summary)