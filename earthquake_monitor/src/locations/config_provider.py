from .base import ILocationProvider
from configs import DEFAULT_LATITUDE, DEFAULT_LONGITUDE
from earthquake_logger import get_logger

log = get_logger(__name__)

class ConfigLocationProvider(ILocationProvider):
    def get_location(self) -> dict:
        log.warning("Using fallback location from local config.")
        return {'lat': DEFAULT_LATITUDE, 'lon': DEFAULT_LONGITUDE}