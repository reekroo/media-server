import logging
import time
from datetime import date, datetime

from .base import IWeatherProvider
from utils.http_client import HttpClient
from models.weather_data import WeatherData

class OpenWeatherMapProvider(IWeatherProvider):
    BASE_URL = 'https://api.openweathermap.org/data/2.5/weather'
    ONECALL_URL = 'https://api.openweathermap.org/data/3.0/onecall'

    def __init__(self, api_key: str, http_client: HttpClient, logger: logging.Logger):
        self._api_key = api_key
        self._http_client = http_client
        self.log = logger

    def get_current_weather(self, lat: float, lon: float) -> list | None:

        params = {'lat': lat, 'lon': lon, 'appid': self._api_key, 'units': 'metric', 'lang': 'ru'}
        try:
            self.log.info(f"Request to OpenWeatherMap for location {lat},{lon}...")
            data = self._http_client.get_json(self.BASE_URL, params=params)
            self.log.info("OpenWeatherMap data received successfully.")

            current_weather = {
                "date": date.today().strftime('%Y-%m-%d'),
                "avg_temp_c": data['main']['temp'],
                "condition": data['weather'][0]['description'],
                "wind_speed_mps": data['wind']['speed'],
                "humidity": data['main']['humidity'],
            }
            return [current_weather]
        
        except Exception as e:
            self.log.error(f"Failed to get weather from OpenWeatherMap: {e}")
            return None

    def get_forecast(self, lat: float, lon: float) -> list | None:
        params = {
            'lat': lat, 'lon': lon, 'appid': self._api_key, 'units': 'metric',
            'lang': 'ru', 'exclude': 'current,minutely,hourly,alerts'
        }
        try:
            self.log.info(f"Requesting 8-day forecast from OpenWeatherMap for {lat},{lon}...")
            data = self._http_client.get_json(self.ONECALL_URL, params=params)

            simplified_forecast = []
            for day_data in data.get('daily', []):
                simplified_forecast.append({
                    "date": date.fromtimestamp(day_data.get('dt')).strftime('%Y-%m-%d'),
                    "max_temp_c": day_data.get('temp', {}).get('max'),
                    "min_temp_c": day_data.get('temp', {}).get('min'),
                    "condition": day_data.get('weather', [{}])[0].get('description'),
                    "chance_of_rain_percent": int(day_data.get('pop', 0) * 100),
                })
            return simplified_forecast
        
        except Exception as e:
            self.log.error(f"Failed to get forecast from OpenWeatherMap: {e}")
            return None

    def get_historical(self, lat: float, lon: float, requested_date: date) -> list | None:
        timestamp = int(time.mktime(requested_date.timetuple()))
        params = {'lat': lat, 'lon': lon, 'dt': timestamp, 'appid': self._api_key, 'units': 'metric', 'lang': 'ru'}
        try:
            self.log.info(f"Requesting historical data from OpenWeatherMap for {lat},{lon} on {requested_date}...")
            data = self._http_client.get_json(f"{self.ONECALL_URL}/timemachine", params=params)

            day_data = data.get('data', [{}])[0]
            simplified_historical = {
                "date": requested_date.strftime('%Y-%m-%d'),
                "avg_temp_c": day_data.get('temp'),
                "condition": day_data.get('weather', [{}])[0].get('description'),
                "total_precip_mm": day_data.get('rain', {}).get('1h', 0)
            }
            return [simplified_historical]
        
        except Exception as e:
            self.log.error(f"Failed to get historical data from OpenWeatherMap: {e}")
            return None