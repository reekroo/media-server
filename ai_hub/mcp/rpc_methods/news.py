import tomllib
from pathlib import Path
from mcp.context import AppContext
from functions.feeds.feed_collector import FeedCollector

async def build_digest(app: AppContext, config_name: str, section: str | None = None) -> None:
    """
    Универсальный метод для сборки и отправки новостных дайджестов.
    Оркестрирует сбор, LLM-суммаризацию и отправку на основе TOML-конфигурации.
    """
    print(f"Executing job: news.build_digest for config '{config_name}'")

    config_path = app.settings.BASE_DIR / "configs" / f"{config_name}.toml"
    if not config_path.exists():
        print(f"Warning: Config file not found at {config_path}")
        return

    cfg = tomllib.loads(config_path.read_text("utf-8"))
    if not cfg.get("enabled", False):
        return

    async with FeedCollector() as collector:
        for sec_name, sec_config in cfg.get("feeds", {}).items():
            if section and section != sec_name:
                continue

            items = await collector.collect(
                urls=sec_config.get("urls", []),
                max_items=cfg.get("max_items", 20)
            )
            if not items:
                continue

            ai_topic = cfg.get("ai_topic", config_name)
            summary_text = await app.ai_service.digest(
                kind=ai_topic,
                params={'items': [item.__dict__ for item in items], 'section': sec_name}
            )

            render_template = cfg.get("render_template", "🗞️ {section}\n{summary}")
            message = render_template.format(section=sec_name.capitalize(), summary=summary_text)

            channel = app.channel_factory.get_channel(cfg.get("to", "telegram"))
            await channel.send(destination=cfg.get("destination"), content=message)
            print(f"Digest '{config_name}/{sec_name}' sent successfully.")