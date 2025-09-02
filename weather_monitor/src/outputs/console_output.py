import logging
from .base import IOutputStrategy
from models.weather_data import WeatherData

class ConsoleOutput(IOutputStrategy):
    def __init__(self, logger: logging.Logger):
        self._log = logger

    def output(self, data: WeatherData):
        self._log.info("--- CURRENT WEATHER (CONSOLE) ---")
        self._log.info(f"Source: {data.source}")
        self._log.info(f"Location: {data.location_name}")
        self._log.info(f"Temperature: {data.temperature}°C (feels like {data.feels_like}°C)")
        self._log.info(f"Condition: {data.description}")
        self._log.info(f"Humidity: {data.humidity}%")
        self._log.info(f"Pressure: {data.pressure} hPa")
        self._log.info("---------------------------------")