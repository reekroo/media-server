import logging
from datetime import date
from typing import List, Optional

from models.weather_data import WeatherData
from providers.base import IWeatherProvider

class OnDemandWeatherService:
    def __init__(self,
                 weather_providers: List[IWeatherProvider],
                 logger: logging.Logger):
        self._weather_providers = weather_providers
        self._log = logger

    def _get_weather_with_fallback(self, lat: float, lon: float) -> Optional[WeatherData]:
        for provider in self._weather_providers:
            provider_name = provider.__class__.__name__
            self._log.info(f"On-demand: Attempting to fetch weather from {provider_name} for coords ({lat}, {lon})...")
            data = provider.get_current_weather(lat, lon)
            if data:
                return data
            self._log.warning(f"On-demand: Failed to get data from {provider_name}.")
        return None

    def get_weather_for_coords_and_date(self, lat: float, lon: float, requested_date: date) -> Optional[WeatherData]:
        if requested_date != date.today():
            self._log.warning(
                f"Received request for non-current date ({requested_date}). This is not yet implemented."
            )
            return None

        self._log.info(f"On-demand request for coords ({lat}, {lon}) on {requested_date}.")
        weather_data = self._get_weather_with_fallback(lat, lon)
        
        if not weather_data:
            self._log.error(f"On-demand: Failed to get weather for coords ({lat}, {lon}) from all providers.")
            return None
        
        self._log.info(f"On-demand: Successfully fetched weather for coords ({lat}, {lon}).")
        return weather_data