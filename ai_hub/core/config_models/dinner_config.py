from typing import List, Optional
from pydantic import Field

from .base_message_target_config import MessageTargetConfig

class DinnerConfig(MessageTargetConfig):
    generate_image: Optional[bool] = False
    render_template: str = "👩‍🍳 What's for Dinner?\n\n{summary}"
    
    max_prep_time_minutes: int = 20
    max_cook_time_minutes: int = 45
    exclude_ingredients: List[str] = Field(default_factory=lambda: ["pork", "shrimp"])
    cuisine: str = "Mediterranean, Italian, simple European, Turkish, Belarus"
    other: str = "Kid-friendly, not too spicy, healthy, can be cooked in one pan if possible"