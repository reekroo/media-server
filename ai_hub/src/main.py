import asyncio, argparse
from pathlib import Path
from src.core.settings import Settings
from src.core.agents.factory import agent_factory
from src.core.router import Orchestrator
from src.topics.weather import WeatherSummary
from src.topics.quakes import QuakesAssessment
from src.topics.movies import MoviesRecommend
from src.digests.brief.composer import build_daily_brief
from src.digests.media.collector import collect_new_titles
from src.digests.media.recommender import build_media_recommendations
from src.digests.media.templates import render_media_digest
from src.digests.sys.build import build_system_digest
from src.channels.telegram_send.telegram_send import send_text as tg_send

def build_orchestrator(settings: Settings) -> Orchestrator:
    agent = agent_factory(api_key=settings.GEMINI_API_KEY)
    topics = {
        "weather.summary": WeatherSummary(),
        "quakes.assess": QuakesAssessment(),
        "movies.recommend": MoviesRecommend(),
    }
    return Orchestrator(agent, topics)

async def run_brief(send_to: str):
    s = Settings()
    orch = build_orchestrator(s)
    txt = await build_daily_brief(orch, s.WEATHER_JSON, s.QUAKES_JSON)
    if send_to == "telegram" and s.TELEGRAM_BOT_TOKEN and s.TELEGRAM_CHAT_ID:
        await tg_send(s.TELEGRAM_BOT_TOKEN, s.TELEGRAM_CHAT_ID, txt)
    else:
        print(txt)

async def run_media(send_to: str):
    s = Settings()
    import tomllib
    cfg = tomllib.loads(Path("configs/media.toml").read_text("utf-8"))
    new_titles = collect_new_titles(
        root=Path(cfg.get("root", str(s.MOVIES_ROOT))),
        state_path=Path(cfg.get("state_path", "state/media_index.json")),
        include_ext=cfg.get("include_ext", [".mkv",".mp4",".avi",".mov"]),
        max_depth=int(cfg.get("max_depth", 6)),
    )
    orch = build_orchestrator(s)
    rec_text = await build_media_recommendations(
        orch, root=Path(cfg.get("root", str(s.MOVIES_ROOT))), prefs=cfg.get("recommender", {})
    )
    msg = render_media_digest(new_titles=new_titles, recommend_text=rec_text, soon_text=None)
    if send_to == "telegram" and s.TELEGRAM_BOT_TOKEN and s.TELEGRAM_CHAT_ID:
        await tg_send(s.TELEGRAM_BOT_TOKEN, s.TELEGRAM_CHAT_ID, msg)
    else:
        print(msg)

async def run_sys(send_to: str):
    s = Settings()
    _, msg = build_system_digest(
        config_path=Path("configs/sys.toml"),
        incidents_dir=Path("state/incidents"),
        state_path=Path("state/sys_digest.json"),
    )
    if send_to == "telegram" and s.TELEGRAM_BOT_TOKEN and s.TELEGRAM_CHAT_ID:
        await tg_send(s.TELEGRAM_BOT_TOKEN, s.TELEGRAM_CHAT_ID, msg)
    else:
        print(msg)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["brief","media","sys"])
    ap.add_argument("--to", choices=["console","telegram"], default="console")
    args = ap.parse_args()
    if args.cmd == "brief": asyncio.run(run_brief(args.to))
    elif args.cmd == "media": asyncio.run(run_media(args.to))
    else: asyncio.run(run_sys(args.to))

if __name__ == "__main__":
    main()
