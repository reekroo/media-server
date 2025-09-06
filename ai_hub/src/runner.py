from __future__ import annotations
import asyncio, zoneinfo, os
from pathlib import Path
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from .core.settings import Settings
from .core.agents.factory import agent_factory
from .core.router import Orchestrator
from .topics.weather import WeatherSummary
from .topics.quakes import QuakesAssessment
from .topics.movies import MoviesRecommend
from .digests.brief.composer import build_daily_brief
from .digests.media.collector import collect_new_titles
from .digests.media.recommender import build_media_recommendations
from .digests.media.templates import render_media_digest
from .digests.sys.build import build_system_digest
from .channels.console.console import send_to_console
from .channels.telegram_send.telegram_send import send_text as tg_send

def build_orchestrator(settings: Settings) -> Orchestrator:
    agent = agent_factory(api_key=settings.GEMINI_API_KEY)
    topics = {"weather.summary": WeatherSummary(),"quakes.assess": QuakesAssessment(),"movies.recommend": MoviesRecommend()}
    return Orchestrator(agent, topics)

async def job_daily_brief(settings: Settings):
    orch = build_orchestrator(settings)
    import tomllib
    cfg = tomllib.loads(Path('configs/daily.toml').read_text('utf-8')) if Path('configs/daily.toml').exists() else {}
    include_q = bool(cfg.get('brief', {}).get('include_quakes', True))
    qpath = Path(cfg.get('quakes_json', str(settings.QUAKES_JSON))) if cfg.get('quakes_json') else settings.QUAKES_JSON
    wpath = Path(cfg.get('weather_json', str(settings.WEATHER_JSON))) if cfg.get('weather_json') else settings.WEATHER_JSON
    txt = await build_daily_brief(orch, wpath, qpath, include_quakes=include_q)
    if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID:
        await tg_send(settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID, txt)
    else:
        send_to_console(txt)

async def job_media_digest(settings: Settings):
    cfg_path = Path("configs/media.toml"); import tomllib
    cfg = tomllib.loads(cfg_path.read_text("utf-8")) if cfg_path.exists() else {}
    root = Path(cfg.get("root", str(settings.MOVIES_ROOT)))
    include_ext = cfg.get("include_ext", [".mkv",".mp4",".avi",".mov"])
    state_path = Path(cfg.get("state_path", "state/media_index.json"))
    max_depth = int(cfg.get("max_depth", 6))
    new_titles = collect_new_titles(root=root, state_path=state_path, include_ext=include_ext, max_depth=max_depth)
    orch = build_orchestrator(settings); prefs = cfg.get("recommender", {})
    rec_text = await build_media_recommendations(orch, root=root, prefs=prefs, cap=cfg.get("cap", 600))
    msg = render_media_digest(new_titles=new_titles, recommend_text=rec_text, soon_text=None)
    if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID:
        await tg_send(settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID, msg)
    else:
        send_to_console(msg)

async def job_sys_digest(settings: Settings):
    digest, msg = build_system_digest(config_path=Path("configs/sys.toml"), incidents_dir=Path("state/incidents"), state_path=Path("state/sys_digest.json"))
    if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID:
        await tg_send(settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID, msg)
    else:
        send_to_console(msg)

async def _async_main():
    s = Settings()
    tz = zoneinfo.ZoneInfo(s.TZ)
    sched = AsyncIOScheduler(timezone=tz)

    # расписания
    sched.add_job(lambda: asyncio.create_task(job_daily_brief(s)),
                  CronTrigger(hour=8, minute=30),
                  id="daily_brief", coalesce=True, misfire_grace_time=600)

    sched.add_job(lambda: asyncio.create_task(job_media_digest(s)),
                  CronTrigger(hour=19, minute=0),
                  id="media_digest", coalesce=True, misfire_grace_time=600)

    sched.add_job(lambda: asyncio.create_task(job_sys_digest(s)),
                  CronTrigger(hour="9,15,21", minute=0),
                  id="sys_digest", coalesce=True, misfire_grace_time=600)

    # если у тебя в файле есть _register_extra_jobs(sched, s) для news/gaming — не забудь вызвать:
    try:
        _register_extra_jobs  # type: ignore[name-defined]
        _register_extra_jobs(sched, s)  # type: ignore[misc]
    except NameError:
        pass

    sched.start()

    # держим цикл живым
    stop = asyncio.Event()
    try:
        await stop.wait()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        sched.shutdown(wait=False)

def main():
    asyncio.run(_async_main())

if __name__ == "__main__":
    main()



from .topics.news import NewsDigestTopic
from .topics.gaming import GamingDigestTopic
from .digests.news.collector import collect_feeds as collect_news
from .digests.news.templates import render_news_digest
from .digests.gaming.collector import collect_feeds as collect_gaming
from .digests.gaming.templates import render_gaming_digest

import tomllib

async def job_news_digest(settings: Settings):
    cfgp = Path("configs/news.toml")
    if not cfgp.exists(): return
    cfg = tomllib.loads(cfgp.read_text("utf-8"))
    if not cfg.get("enabled", False): return
    max_items = int(cfg.get("max_items", 20))
    orch = build_orchestrator(settings)
    # For each section in feeds
    feeds = cfg.get("feeds", {})
    topic = NewsDigestTopic()
    for section, urls in (feeds or {}).items():
        items = collect_news(list(urls), max_items=max_items)
        if not items: continue
        prompt_payload = {"items": items, "section": section}
        text = await orch.run("news.digest", prompt_payload) if "news.digest" in orch.topics else await topic.postprocess(await orch.agent.generate(topic.build_prompt(prompt_payload)))
        msg = render_news_digest(section, text)
        if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID:
            await tg_send(settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID, msg)
        else:
            send_to_console(msg)

async def job_gaming_digest(settings: Settings):
    cfgp = Path("configs/gaming.toml")
    if not cfgp.exists(): return
    cfg = tomllib.loads(cfgp.read_text("utf-8"))
    if not cfg.get("enabled", False): return
    max_items = int(cfg.get("max_items", 20))
    orch = build_orchestrator(settings)
    feeds = cfg.get("feeds", {})
    topic = GamingDigestTopic()
    items = []
    for _, urls in (feeds or {}).items():
        items.extend(collect_gaming(list(urls), max_items=max_items))
    if not items: return
    payload = {"items": items[:max_items]}
    text = await orch.run("gaming.digest", payload) if "gaming.digest" in orch.topics else await topic.postprocess(await orch.agent.generate(topic.build_prompt(payload)))
    msg = render_gaming_digest(text)
    if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_CHAT_ID:
        await tg_send(settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID, msg)
    else:
        send_to_console(msg)

# register extra jobs
def _register_extra_jobs(sched, s):
    sched.add_job(lambda: asyncio.create_task(job_news_digest(s)),  CronTrigger(hour=10, minute=0), id="news_digest", coalesce=True, misfire_grace_time=600)
    sched.add_job(lambda: asyncio.create_task(job_gaming_digest(s)), CronTrigger(hour=11, minute=0), id="gaming_digest", coalesce=True, misfire_grace_time=600)
