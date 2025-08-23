import requests
from .base import IWeatherProvider, WeatherData
from weather_logger import get_logger

log = get_logger(__name__)


class OpenWeatherMapProvider(IWeatherProvider):
    def __init__(self, api_key: str):
        self._api_key = api_key
        self._base_url = "https://api.openweathermap.org/data/2.5/weather"

    def get_current_weather(self, lat: float, lon: float) -> WeatherData | None:
        
        location_query = f"{lat},{lon}"
        log.info(f"Request to OpenWeatherMap for the locatıon {location_query}...")

        params = {
            'lat': lat, 
            'lon': lon, 
            'appid': self._api_key, 
            'units': 'metric', 
            'lang': 'ru'
        }

        try:
            response = requests.get(self._base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            log.info("OpenWeatherMap no data.")
            return self._map_to_weather_data(data)
        
        except requests.exceptions.RequestException as e:
            log.error(f"Error OpenWeatherMap: {e}")
            return None

    def _map_to_weather_data(self, data: dict) -> WeatherData:
        return WeatherData(
            location_name=data['name'],
            temperature=data['main']['temp'],
            feels_like=data['main']['feels_like'],
            pressure=data['main']['pressure'],
            humidity=data['main']['humidity'],
            description=data['weather'][0]['description'].capitalize(),
            source='OpenWeatherMap'
        )