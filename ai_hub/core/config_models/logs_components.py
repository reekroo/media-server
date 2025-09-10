from typing import List

from pydantic import BaseModel

class LogComponentConfig(BaseModel):
    log_dir: str
    error_patterns: List[str]

class ComponentsConfig(BaseModel):
    backup_service: LogComponentConfig
    earthquake_monitor: LogComponentConfig
    location_service: LogComponentConfig
    metrics_exporter: LogComponentConfig
    weather_monitor: LogComponentConfig
    peripheral_scripts: LogComponentConfig