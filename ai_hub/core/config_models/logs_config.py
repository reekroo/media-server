from typing import Optional

from .logs_components import ComponentsConfig
from .message_target_config import MessageTargetConfig

class LogsConfig(MessageTargetConfig):    
    generate_image: Optional[bool] = False
    render_template: str = "📊 Log Analytics Digest\n\n{summary}"
    
    lookback_hours: int = 24
    components: ComponentsConfig