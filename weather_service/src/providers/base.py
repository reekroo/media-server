from abc import ABC, abstractmethod
from models.weather_data import WeatherData

class IWeatherProvider(ABC):
    
    @abstractmethod
    def get_current_weather(self, lat: float, lon: float) -> WeatherData | None:
        pass