from abc import ABC, abstractmethod

class ILocationProvider(ABC):
    @abstractmethod
    def determine_location(self) -> dict | None:
        pass