import logging
from providers.nominatim_provider import NominatimProvider

class GeocodingService:
    def __init__(self, provider: NominatimProvider, logger: logging.Logger):
        self._provider = provider
        self.log = logger

    def geocode_city(self, city_name: str) -> dict:
        self.log.info(f"Geocoding service: Request to geocode '{city_name}'")
        return self._provider.determine_location(city_name=city_name)