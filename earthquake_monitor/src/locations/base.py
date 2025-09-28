from abc import ABC, abstractmethod
from typing import Dict, Optional

class ILocationProvider(ABC):
    @abstractmethod
    async def get_location(self) -> Optional[Dict[str, float]]:
        pass