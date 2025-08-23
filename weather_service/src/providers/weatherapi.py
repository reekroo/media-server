import requests
from .base import IWeatherProvider, WeatherData
from weather_logger import get_logger

log = get_logger(__name__)

class WeatherApiProvider(IWeatherProvider):

    def __init__(self, api_key: str):
        self._api_key = api_key
        self._base_url = "http://api.weatherapi.com/v1/current.json"

    def get_current_weather(self, lat: float, lon: float) -> WeatherData | None:

        location_query = f"{lat},{lon}"
        log.info(f"Request to WeatherAPI for the locatıon {location_query}...")

        params = {
            'key': self._api_key, 
            'q': location_query, 
            'aqi': 'no'
        }
        
        try:
            response = requests.get(self._base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            log.info("WeatherAPI no data.")
            return self._map_to_weather_data(data)
        
        except requests.exceptions.RequestException as e:
            log.error(f"Error WeatherAPI: {e}")
            return None

    def _map_to_weather_data(self, data: dict) -> WeatherData:
        return WeatherData(
            location_name=data['location']['name'],
            temperature=data['current']['temp_c'],
            feels_like=data['current']['feelslike_c'],
            pressure=data['current']['pressure_mb'],
            humidity=data['current']['humidity'],
            description=data['current']['condition']['text'],
            source='WeatherAPI'
        )