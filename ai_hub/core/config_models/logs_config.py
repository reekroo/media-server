from typing import Optional
from pydantic import BaseModel

from .logs_components import ComponentsConfig

class LogsConfig(BaseModel):
    enabled: bool = True
    to: str = "telegram"
    destination: str = ""
    destination_language: Optional[str] = None
    generate_image: Optional[bool] = False
    render_template: str = "📊 Log Analytics Digest\n\n{summary}"
    
    lookback_hours: int = 24
    components: ComponentsConfig