import logging
import time
from datetime import date, datetime, timezone

from .base import IWeatherProvider
from utils.http_client import HttpClient
from models.weather_data import WeatherData
from models.api_responses import (
    ForecastResponse, 
    ForecastDay, 
    HistoricalResponse, 
    HistoricalHour
)

class OpenWeatherMapProvider(IWeatherProvider):
    BASE_URL = 'https://api.openweathermap.org/data/2.5/weather'
    ONECALL_URL = 'https://api.openweathermap.org/data/3.0/onecall'

    def __init__(self, api_key: str, http_client: HttpClient, logger: logging.Logger):
        self._api_key = api_key
        self._http_client = http_client
        self.log = logger

    def get_current_weather(self, lat: float, lon: float) -> WeatherData | None:
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self._api_key,
            'units': 'metric',
            'lang': 'ru'
        }
        try:
            self.log.info(f"Request to OpenWeatherMap for location {lat},{lon}...")
            data = self._http_client.get_json(self.BASE_URL, params=params)
            self.log.info("OpenWeatherMap data received successfully.")
            return WeatherData(
                location_name=data['name'],
                temperature=data['main']['temp'],
                feels_like=data['main']['feels_like'],
                pressure=data['main']['pressure'],
                humidity=data['main']['humidity'],
                description=data['weather'][0]['description'],
                wind_speed=data['wind']['speed'],
                source=self.__class__.__name__
            )
        except Exception as e:
            self.log.error(f"Failed to get weather from OpenWeatherMap: {e}")
            return None

    def get_forecast(self, lat: float, lon: float) -> dict | None:
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self._api_key,
            'units': 'metric',
            'lang': 'ru',
            'exclude': 'current,minutely,hourly,alerts'
        }
        try:
            self.log.info(f"Requesting 8-day forecast from OpenWeatherMap for {lat},{lon}...")
            data = self._http_client.get_json(self.ONECALL_URL, params=params)
            return data.get('forecast', {}).get('forecastday')
        except Exception as e:
            self.log.error(f"Failed to get forecast from OpenWeatherMap: {e}")
            return None

    def get_historical(self, lat: float, lon: float, requested_date: date) -> dict | None:
        timestamp = int(time.mktime(requested_date.timetuple()))
        params = {
            'lat': lat,
            'lon': lon,
            'dt': timestamp,
            'appid': self._api_key,
            'units': 'metric',
            'lang': 'ru'
        }
        try:
            self.log.info(f"Requesting historical data from OpenWeatherMap for {lat},{lon} on {requested_date}...")
            data = self._http_client.get_json(f"{self.ONECALL_URL}/timemachine", params=params)
            return data.get('forecast', {}).get('forecastday')
        except Exception as e:
            self.log.error(f"Failed to get historical data from OpenWeatherMap: {e}")
            return None