from abc import ABC, abstractmethod

class BaseAlerter(ABC):
    
    @abstractmethod
    def alert(self, level: int, magnitude: float, location: str):
        pass