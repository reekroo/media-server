import logging
from .base import ILocationProvider
from utils.http_client import HttpClient

class NominatimProvider(ILocationProvider):
    URL = 'https://nominatim.openstreetmap.org/search'

    def __init__(self, http_client: HttpClient, logger: logging.Logger):
        self._http_client = http_client
        self.log = logger

    def determine_location(self, city_name: str) -> dict | None:
        try:
            self.log.info(f"Attempting to geocode city '{city_name}' via Nominatim...")
            params = {'q': city_name, 'format': 'json', 'limit': 1}
            headers = {'User-Agent': 'LocationService/1.0'}
            
            data = self._http_client.get_json(self.URL, params=params, headers=headers)
            
            if not data:
                self.log.warning(f"No results found for city: {city_name}")
                return None

            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])
            self.log.info(f"Successfully geocoded '{city_name}': ({lat}, {lon})")
            
            return {'status': 'success', 'lat': lat, 'lon': lon}
        except Exception as e:
            self.log.error(f"Failed to get location from Nominatim for '{city_name}': {e}")
            return {'status': 'error', 'message': str(e)}

    def get_location(self) -> dict | None:
        self.log.warning("NominatimProvider cannot be called without a city_name.")
        return None