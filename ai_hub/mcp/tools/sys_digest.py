from __future__ import annotations
from src.app import App

async def system_digest(app: App, config: str = "configs/sys.toml") -> str:
    return await app.run_sys_digest(config_path_override=config)