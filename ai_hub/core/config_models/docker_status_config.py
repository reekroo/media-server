from typing import List, Optional
from pydantic import BaseModel, Field

class DockerStatusConfig(BaseModel):
    enabled: bool = True
    to: str = "telegram"
    destination: str = ""
    destination_topic: Optional[str] = None
    destination_language: Optional[str] = None
    generate_image: Optional[bool] = False
    render_template: str = "🐳 Docker Status Digest\n\n{summary}"

    ignore_containers: List[str] = Field(default_factory=list)