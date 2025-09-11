from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class TomlMetadata:
    key: Optional[str] = None