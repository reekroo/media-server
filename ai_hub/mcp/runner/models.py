from dataclasses import dataclass
from typing import Optional

@dataclass
class DeliveryItem:
    original_text: str
    generate_image: bool
    target_lang: Optional[str]