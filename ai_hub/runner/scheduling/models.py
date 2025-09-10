from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Any, Dict

@dataclass
class JobConfig:
    job: Optional[str]
    cron: str
    enabled: bool = True
    to: str = "telegram"
    coalesce: bool = True
    max_instances: int = 1
    misfire_grace_time: int = 60
    jitter: Optional[int] = None

    @staticmethod
    def from_dict(section: str, data: Dict[str, Any], fallback_job: Optional[str]) -> "JobConfig":
        if not isinstance(data, dict):
            raise ValueError(f"Section [{section}] must be a table (dict), got {type(data).__name__}")
        
        cron = (data.get("cron") or "").strip()
        
        if not cron:
            raise ValueError(f"Section [{section}] is enabled but has no 'cron' field")

        enabled = bool(data.get("enabled", True))
        job = data.get("job")
        
        if job is None:
            job = fallback_job or section

        to = (data.get("to") or "telegram").strip() or "telegram"
        coalesce = bool(data.get("coalesce", True))
        max_instances = int(data.get("max_instances", 1))
        misfire_grace_time = int(data.get("misfire_grace_time", 60))
        jitter = data.get("jitter")
        
        if jitter is not None:
            jitter = int(jitter)

        return JobConfig(
            job=job,
            cron=cron,
            enabled=enabled,
            to=to,
            coalesce=coalesce,
            max_instances=max_instances,
            misfire_grace_time=misfire_grace_time,
            jitter=jitter,
        )
