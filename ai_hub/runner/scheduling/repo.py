from __future__ import annotations

from pathlib import Path
from typing import Dict, Any

import tomllib

from .models import JobConfig

class ScheduleRepository:
    def load(self) -> Dict[str, JobConfig]:
        raise NotImplementedError

class TomlScheduleRepository(ScheduleRepository):
    def __init__(self, path: Path, fallback_mapping: Dict[str, str] | None = None) -> None:
        self.path = path
        self.fallback_mapping = fallback_mapping or {}

    def _read_raw(self) -> Dict[str, Any]:
        if not self.path.exists():
            return {}
        
        with self.path.open("rb") as f:
            data = tomllib.load(f)
        
        return data or {}

    def load(self) -> Dict[str, JobConfig]:
        raw = self._read_raw()
        result: Dict[str, JobConfig] = {}

        for section, cfg in raw.items():
            if not isinstance(cfg, dict):
                continue
            fb_job = self.fallback_mapping.get(section, section)
            try:
                jc = JobConfig.from_dict(section, cfg, fb_job)
            except Exception:
                continue
            result[section] = jc
        
        return result
