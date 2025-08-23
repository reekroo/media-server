from abc import ABC, abstractmethod

class DataSource(ABC):

    @abstractmethod
    def get_earthquakes(self, latitude, longitude):
        pass