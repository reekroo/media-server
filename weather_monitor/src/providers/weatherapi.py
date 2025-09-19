import logging
from datetime import date

from .base import IWeatherProvider
from utils.http_client import HttpClient
from models.weather_data import WeatherData
from models.api_responses import (
    ForecastResponse, 
    ForecastDay, 
    HistoricalResponse, 
    HistoricalHour
)
class WeatherApiProvider(IWeatherProvider):
    BASE_URL = 'http://api.weatherapi.com/v1'

    def __init__(self, api_key: str, http_client: HttpClient, logger: logging.Logger):
        self._api_key = api_key
        self._http_client = http_client
        self.log = logger

    def get_current_weather(self, lat: float, lon: float) -> WeatherData | None:
        url = f"{self.BASE_URL}/current.json"
        params = {
            'key': self._api_key,
            'q': f"{lat},{lon}",
            'lang': 'ru'
        }
        try:
            self.log.info(f"Request to WeatherAPI for location {lat},{lon}...")
            data = self._http_client.get_json(url, params=params)
            self.log.info("WeatherAPI data received successfully.")
            return WeatherData(
                location_name=data['location']['name'],
                temperature=data['current']['temp_c'],
                feels_like=data['current']['feelslike_c'],
                pressure=data['current']['pressure_mb'],
                humidity=data['current']['humidity'],
                description=data['current']['condition']['text'],
                wind_speed=round(data['current']['wind_kph'] * 1000 / 3600, 2),
                source=self.__class__.__name__
            )
        except Exception as e:
            self.log.error(f"Failed to get weather from WeatherAPI: {e}")
            return None

    def get_forecast(self, lat: float, lon: float, days: int = 7) -> dict | None:
        url = f"{self.BASE_URL}/forecast.json"
        params = {
            'key': self._api_key,
            'q': f"{lat},{lon}",
            'days': days,
            'lang': 'ru'
        }
        try:
            self.log.info(f"Requesting {days}-day forecast from WeatherAPI for {lat},{lon}...")
            data = self._http_client.get_json(url, params=params)
            return data.get('forecast', {}).get('forecastday')
        except Exception as e:
            self.log.error(f"Failed to get forecast from WeatherAPI: {e}")
            return None

    def get_historical(self, lat: float, lon: float, requested_date: date) -> dict | None:
        url = f"{self.BASE_URL}/history.json"
        params = {
            'key': self._api_key,
            'q': f"{lat},{lon}",
            'dt': requested_date.strftime('%Y-%m-%d')
        }
        try:
            self.log.info(f"Requesting historical data from WeatherAPI for {lat},{lon} on {requested_date}...")
            data = self._http_client.get_json(url, params=params)
            return data.get('forecast', {}).get('forecastday')
        except Exception as e:
            self.log.error(f"Failed to get historical data from WeatherAPI: {e}")
            return None