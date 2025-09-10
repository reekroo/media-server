from typing import List
from pydantic import BaseModel, Field

class DinnerConfig(BaseModel):
    cuisine: str ="Mediterranean, Italian, simple European, Turkish, Belarus"
    exclude_ingredients: List[str] = Field(default_factory=lambda: ["pork", "shrimp"])
    max_prep_time_minutes: int = 20
    max_cook_time_minutes: int = 45
    other: str ="Kid-friendly, not too spicy, healthy, can be cooked in one pan if possible"