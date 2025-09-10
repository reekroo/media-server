import tomllib
from pathlib import Path
import asyncio

from mcp.context import AppContext
from functions.logs.collector import LogCollector

async def build_digest(app: AppContext, config_name: str) -> None:
    """Собирает и анализирует логи компонентов, отправляет дайджест."""
    print(f"Executing job: logs.build_digest for config '{config_name}'")

    config_path = app.settings.BASE_DIR / "configs" / f"{config_name}.toml"
    if not config_path.exists():
        return
    cfg = tomllib.loads(config_path.read_text("utf-8"))
    if not cfg.get("enabled", False):
        return

    collector = LogCollector()
    tasks = []
    for name, params in cfg.get("components", {}).items():
        task = collector.analyze_directory(
            log_dir=Path(params["log_dir"]),
            patterns=params.get("error_patterns", []),
            lookback_hours=cfg.get("lookback_hours", 24)
        )
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)

    warn_reports = [res.model_dump() for res in results if res.status == "WARN"]

    summary_text: str
    if not warn_reports:
        summary_text = "All monitored components are nominal. No new errors found in logs."
    else:
        summary_text = await app.ai_service.digest(
            kind='logs',
            params={'reports': warn_reports}
        )

    render_template = cfg.get("render_template", "📊 Log Analytics Digest\n\n{summary}")
    message = render_template.format(summary=summary_text)

    channel = app.channel_factory.get_channel(cfg.get("to", "telegram"))
    await channel.send(destination=cfg.get("destination"), content=message)
    print(f"Digest '{config_name}' sent successfully.")