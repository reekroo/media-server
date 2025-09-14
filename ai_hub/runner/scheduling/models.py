from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Any, Dict, List, Union

@dataclass
class JobConfig:
    job: Optional[str]
    cron: str
    crons: List[str]
    enabled: bool = True
    to: str = "telegram"
    coalesce: bool = True
    max_instances: int = 1
    misfire_grace_time: int = 60
    jitter: Optional[int] = None

    def cron_list(self) -> List[str]:
        if self.crons:
            return [s.strip() for s in self.crons if isinstance(s, str) and s.strip()]

        return [self.cron.strip()]

    @staticmethod
    def _normalize_crons(data: Dict[str, Any]) -> tuple[str, List[str]]:
        crons_value = data.get("crons")
        if isinstance(crons_value, list) and crons_value:
            crons_list = [str(s).strip() for s in crons_value if str(s).strip()]
            if not crons_list:
                raise ValueError("'crons' provided but empty after normalization")

            return crons_list[0], crons_list

        cron_str = (data.get("cron") or "").strip()
        if not cron_str:
            raise ValueError("no 'cron' or 'crons' field provided")
        return cron_str, []

    @staticmethod
    def from_dict(section: str, data: Dict[str, Any], fallback_job: Optional[str]) -> "JobConfig":
        if not isinstance(data, dict):
            raise ValueError(f"Section [{section}] must be a table (dict), got {type(data).__name__}")

        cron, crons = JobConfig._normalize_crons(data)

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
            crons=crons,
            enabled=enabled,
            to=to,
            coalesce=coalesce,
            max_instances=max_instances,
            misfire_grace_time=misfire_grace_time,
            jitter=jitter,
        )
