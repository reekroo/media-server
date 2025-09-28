import logging

from .base import ILocationProvider

class ConfigLocationProvider(ILocationProvider):
    def __init__(self, logger: logging.Logger, default_lat: float, default_lon: float):
        self._log = logger
        self._default_location = {'lat': default_lat, 'lon': default_lon}

    async def get_location(self) -> dict:
        self._log.warning("Using fallback location from local config.")
        return self._default_location