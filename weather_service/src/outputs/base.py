from abc import ABC, abstractmethod
from models.weather_data import WeatherData

class IOutputStrategy(ABC):
    @abstractmethod
    
    def output(self, data: WeatherData):
        pass
    
    def close(self):
        pass