import logging
from .base import ILocationProvider


class ConfigLocationProvider(ILocationProvider):
    def __init__(self, lat: float, lon: float, logger: logging.Logger):
        self._lat = lat
        self._lon = lon
        self._log = logger
        self._log.info(f"Initialized fallback location provider with coords: {lat}, {lon}")

    def get_location(self) -> dict:
        self._log.warning("Using fallback location from local config.")
        return {'lat': self._lat, 'lon': self._lon}