from pydantic import BaseModel

from logs_components import ComponentsConfig

class LogsConfig(BaseModel):
    enabled: bool = True
    lookback_hours: int = 24
    components: ComponentsConfig