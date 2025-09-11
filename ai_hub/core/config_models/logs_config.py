from pydantic import BaseModel

from .logs_components import ComponentsConfig

class LogsConfig(BaseModel):
    enabled: bool = True
    to: str = "telegram"
    destination: str = ""

    lookback_hours: int = 24
    render_template: str = "📊 Log Analytics Digest\n\n{summary}"
    
    components: ComponentsConfig