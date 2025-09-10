import tomllib
from pathlib import Path

from mcp.context import AppContext

async def build_digest(app: AppContext, config_name: str) -> None:
    """Генерирует и отправляет идеи для ужина на основе конфигурации."""
    print(f"Executing job: dinner.build_digest for config '{config_name}'")

    config_path = app.settings.BASE_DIR / "configs" / f"{config_name}.toml"
    if not config_path.exists():
        return
    cfg = tomllib.loads(config_path.read_text("utf-8"))
    if not cfg.get("enabled", False):
        return

    preferences = cfg.get("preferences", {})
    summary_text = await app.ai_service.digest(
        kind='dinner',
        params={'preferences': preferences}
    )

    render_template = cfg.get("render_template", "👩‍🍳 What's for Dinner?\n\n{summary}")
    message = render_template.format(summary=summary_text)

    channel = app.channel_factory.get_channel(cfg.get("to", "telegram"))
    await channel.send(destination=cfg.get("destination"), content=message)
    print(f"Digest '{config_name}' sent successfully.")