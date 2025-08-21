from abc import ABC, abstractmethod

class BaseDisplayDriver(ABC):
    @abstractmethod
    def clear(self):
        pass

    @abstractmethod
    def show(self, image):
        pass

    @property
    @abstractmethod
    def width(self):
        pass

    @property
    @abstractmethod
    def height(self):
        pass