import logging
from .base import ILocationProvider
from utils.http_client import HttpClient

class IpInfoProvider(ILocationProvider):
    URL = 'https://ipinfo.io/json'

    def __init__(self, http_client: HttpClient, logger: logging.Logger):
        self._http_client = http_client
        self.log = logger

    def determine_location(self) -> dict | None:
        try:
            self.log.info("Attempting to determine location via ipinfo.io...")
            data = self._http_client.get_json(self.URL)
            
            lat, lon = map(float, data['loc'].split(','))
            self.log.info("Successfully determined location from IP: (%s, %s)", lat, lon)
            
            return {'lat': lat, 'lon': lon}
        except Exception as e:
            self.log.error("Failed to get location from ipinfo.io: %s", e)
            return None