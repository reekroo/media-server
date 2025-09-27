from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class SectionParams:
    name: str
    urls: List[str]
    fetch_limit: int
    section_limit: int
    render_template: str
    generate_image: bool