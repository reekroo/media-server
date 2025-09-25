import logging
from datetime import date
from typing import List, Optional, Any

from providers.base import IWeatherProvider
from models.weather_data import WeatherData

class OnDemandWeatherService:
    def __init__(self,
                 weather_providers: List[IWeatherProvider],
                 logger: logging.Logger):
        self._weather_providers = weather_providers
        self._log = logger

    def _call_provider_with_fallback(self, method_name: str, **kwargs) -> Any:
        for provider in self._weather_providers:
            if not hasattr(provider, method_name):
                self._log.warning(f"Provider {provider.__class__.__name__} does not have method {method_name}.")
                continue
                
            provider_name = provider.__class__.__name__
            self._log.info(f"On-demand: Attempting to call '{method_name}' from {provider_name}...")
            
            method_to_call = getattr(provider, method_name)
            data = method_to_call(**kwargs)
            
            if data:
                self._log.info(f"On-demand: Successfully got data from {provider_name}.")
                return data
            
            self._log.warning(f"On-demand: Failed to get data from {provider_name}.")
        return None

    def get_weather_for_coords_and_date(self, lat: float, lon: float, requested_date: date) -> Optional[Any]:
        today = date.today()

        if requested_date > today:
            self._log.info(f"Request is for a future date ({requested_date}). Fetching forecast for ({lat}, {lon}).")
            return self._call_provider_with_fallback(
                method_name='get_forecast',
                lat=lat,
                lon=lon
            )

        elif requested_date < today:
            self._log.info(f"Request is for a past date ({requested_date}). Fetching historical data for ({lat}, {lon}).")
            return self._call_provider_with_fallback(
                method_name='get_historical',
                lat=lat,
                lon=lon,
                requested_date=requested_date
            )

        else:
            self._log.info(f"Request is for today. Fetching current weather for ({lat}, {lon}).")
            return self._call_provider_with_fallback(
                method_name='get_current_weather',
                lat=lat,
                lon=lon
            )