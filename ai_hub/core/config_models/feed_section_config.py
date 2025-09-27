from typing import List, Optional
from pydantic import BaseModel, Field

class FeedSectionSettings(BaseModel):
    urls: List[str] = Field(default_factory=list)
    fetch_limit: Optional[int] = 25
    section_limit: Optional[int] = 3
    render_template: Optional[str] = ""
    generate_image: Optional[bool] = False