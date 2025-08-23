from abc import ABC, abstractmethod

class ILocationProvider(ABC):
    @abstractmethod
    def get_location(self) -> dict | None:
        pass