from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

class FeedBasedConfig(BaseModel):
    enabled: bool = True
    to: str = "telegram"
    destination: str = ""
    destination_topic: Optional[str] = None
    destination_language: Optional[str] = None
    generate_image: Optional[bool] = True
    
    fetch_limit: int = 25
    section_limit: int = 3

    ai_topic: str = ""
    render_template: str = "{summary}"

    # 1) "section": [url1, url2, ...]
    # 2) "section": { "urls": [...], "limit": 5 }
    feeds: Dict[str, Union[List[str], Dict[str, Any]]] = Field(default_factory=dict)