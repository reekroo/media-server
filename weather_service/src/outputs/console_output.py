from .base import IOutputStrategy
from models.weather_data import WeatherData
from weather_logger import get_logger

log = get_logger(__name__)

class ConsoleOutput(IOutputStrategy):
    def output(self, data: WeatherData):
        log.info("--- CURRENT WEATHER ---")
        log.info(f"Source: {data.source}")
        log.info(f"Location: {data.location_name}")
        log.info(f"Temperature: {data.temperature}°C (feels like {data.feels_like}°C)")
        log.info(f"Condition: {data.description}")
        log.info(f"Humidity: {data.humidity}%")
        log.info(f"Pressure: {data.pressure} hPa")
        log.info("-----------------------")