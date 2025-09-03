import logging
from .base import IWeatherProvider
from models.weather_data import WeatherData
from utils.http_client import HttpClient

class WeatherApiProvider(IWeatherProvider):
    def __init__(self, api_key: str, http_client: HttpClient, logger: logging.Logger):
        self._api_key = api_key
        self._http_client = http_client
        self._log = logger
        self._base_url = "http://api.weatherapi.com/v1/current.json"

    def get_current_weather(self, lat: float, lon: float) -> WeatherData | None:
        if not self._api_key:
            self._log.warning("WeatherAPI API key is not set.")
            return None

        location_query = f"{lat},{lon}"
        self._log.info(f"Request to WeatherAPI for the location {location_query}...")

        params = {
            'key': self._api_key,
            'q': location_query,
            'aqi': 'no'
        }

        try:
            data = self._http_client.get(self._base_url, params=params)
            self._log.info("WeatherAPI data received successfully.")
            return self._map_to_weather_data(data)
        except Exception as e:
            self._log.error(f"Error fetching data from WeatherAPI: {e}")
            return None

    def _map_to_weather_data(self, data: dict) -> WeatherData:
        location_data = data.get('location', {})
        current_data = data.get('current', {})
        condition_data = current_data.get('condition', {})

        return WeatherData(
            location_name=location_data.get('name'),
            temperature=current_data.get('temp_c'),
            feels_like=current_data.get('feelslike_c'),
            pressure=current_data.get('pressure_mb'),
            humidity=current_data.get('humidity'),
            description=condition_data.get('text'),
            wind_speed=current_data.get('wind_kph'),
            source='WeatherAPI'
        )