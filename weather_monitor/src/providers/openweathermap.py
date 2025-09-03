import logging
from .base import IWeatherProvider
from models.weather_data import WeatherData
from utils.http_client import HttpClient

class OpenWeatherMapProvider(IWeatherProvider):
    def __init__(self, api_key: str, http_client: HttpClient, logger: logging.Logger):
        self._api_key = api_key
        self._http_client = http_client
        self._log = logger
        self._base_url = "https://api.openweathermap.org/data/2.5/weather"

    def get_current_weather(self, lat: float, lon: float) -> WeatherData | None:
        if not self._api_key:
            self._log.warning("OpenWeatherMap API key is not set.")
            return None

        self._log.info(f"Request to OpenWeatherMap for location {lat},{lon}...")
        params = {
            'lat': lat, 'lon': lon, 'appid': self._api_key,
            'units': 'metric', 'lang': 'ru'
        }
        try:
            data = self._http_client.get(self._base_url, params=params)
            self._log.info("OpenWeatherMap data received successfully.")
            return self._map_to_weather_data(data)
        except Exception as e:
            self._log.error(f"Error fetching data from OpenWeatherMap: {e}")
            return None

    def _map_to_weather_data(self, data: dict) -> WeatherData:
        main_data = data.get('main', {})
        weather_data = data.get('weather', [{}])[0]
        wind_data = data.get('wind', {})

        return WeatherData(
            location_name=data.get('name'),
            temperature=main_data.get('temp'),
            feels_like=main_data.get('feels_like'),
            pressure=main_data.get('pressure'),
            humidity=main_data.get('humidity'),
            description=weather_data.get('description', '').capitalize(),
            wind_speed=wind_data.get('speed'),
            source='OpenWeatherMap'
        )