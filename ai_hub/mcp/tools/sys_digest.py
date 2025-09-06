from __future__ import annotations
from pathlib import Path
from src.digests.sys.build import build_system_digest

def system_digest(config: str = "configs/sys.toml") -> str:
    """
    MCP tool: sys.digest
    params:
      - config: путь к TOML-конфигу системного дайджеста.
    returns: str — отформатированный дайджест системы.
    """
    _, text = build_system_digest(
        config_path=Path(config),
        incidents_dir=Path("state/incidents"),
        state_path=Path("state/sys_digest.json"),
    )
    return text
