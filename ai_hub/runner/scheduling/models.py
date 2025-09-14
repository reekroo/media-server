from dataclasses import dataclass
from typing import Optional, Any, Dict, List, Union

CronValue = Union[str, List[str]]

@dataclass
class JobConfig:
    job: Optional[str]
    cron: CronValue
    enabled: bool = True
    to: str = "telegram"
    coalesce: bool = True
    max_instances: int = 1
    misfire_grace_time: int = 60
    jitter: Optional[int] = None

    def iter_crons(self) -> List[str]:
        if isinstance(self.cron, str):
            return [self.cron.strip()]
        if isinstance(self.cron, list):
            return [str(c).strip() for c in self.cron if str(c).strip()]
        return []

    @staticmethod
    def from_dict(section: str, data: Dict[str, Any], fallback_job: Optional[str]) -> "JobConfig":
        cron = data.get("cron")
        if cron is None:
            raise ValueError(f"[{section}] missing 'cron'")

        return JobConfig(
            job=data.get("job") or fallback_job or section,
            cron=cron,
            enabled=bool(data.get("enabled", True)),
            to=data.get("to", "telegram"),
            coalesce=bool(data.get("coalesce", True)),
            max_instances=int(data.get("max_instances", 1)),
            misfire_grace_time=int(data.get("misfire_grace_time", 60)),
            jitter=int(data["jitter"]) if "jitter" in data else None,
        )
