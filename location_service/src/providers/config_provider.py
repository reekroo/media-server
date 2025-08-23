from .base import ILocationProvider
from configs import DEFAULT_LATITUDE,DEFAULT_LONGITUDE
from location_logger import get_logger

log = get_logger(__name__)

class ConfigFallbackProvider(ILocationProvider):
    def determine_location(self) -> dict:
        log.warning("Using fallback location from config.")
        return {'lat': DEFAULT_LATITUDE, 'lon': DEFAULT_LONGITUDE}