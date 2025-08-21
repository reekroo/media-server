from abc import ABC, abstractmethod

class BaseScreen(ABC):
    @abstractmethod
    def draw(self, display_manager, stats):
        pass