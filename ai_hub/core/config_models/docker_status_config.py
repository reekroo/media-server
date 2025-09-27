from typing import List, Optional
from pydantic import Field

from .base_message_target_config import MessageTargetConfig

class DockerStatusConfig(MessageTargetConfig):    
    generate_image: Optional[bool] = False
    render_template: str = "🐳 Docker Status Digest\n\n{summary}"

    ignore_containers: List[str] = Field(default_factory=list)