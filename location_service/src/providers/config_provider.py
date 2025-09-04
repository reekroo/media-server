import logging
from .base import ILocationProvider

class ConfigFallbackProvider(ILocationProvider):
    def __init__(self, default_lat: float, default_lon: float, logger: logging.Logger):
        self._location = {'lat': default_lat, 'lon': default_lon}
        self.log = logger
    
    def determine_location(self) -> dict:
        self.log.warning("Using fallback location from config.")
        return self._location