import logging
from typing import List, Optional

from locations.base import ILocationProvider
from providers.base import IWeatherProvider
from outputs.base import IOutputStrategy
from models.weather_data import WeatherData

class PeriodicWeatherService:
    def __init__(self,
                 weather_providers: List[IWeatherProvider],
                 outputs: List[IOutputStrategy],
                 location_providers: List[ILocationProvider],
                 logger: logging.Logger,
                 scheduled_outputs: Optional[List[IOutputStrategy]] = None):
        self._providers = weather_providers
        self._outputs = outputs
        self._scheduled_outputs = scheduled_outputs if scheduled_outputs is not None else []
        self._location_providers = location_providers
        self._log = logger

    def _get_current_location(self) -> dict | None:
        for provider in self._location_providers:
            provider_name = provider.__class__.__name__
            self._log.info(f"Attempting to get location from {provider_name}...")
            location = provider.get_location()
            if location:
                self._log.info(f"Location received from {provider_name}: lat={location.get('lat')}, lon={location.get('lon')}")
                return location
            self._log.warning(f"Failed to get location from {provider_name}.")
        self._log.error("Failed to get location from all available providers.")
        return None

    def _get_weather_with_fallback(self, lat: float, lon: float) -> WeatherData | None:
        for provider in self._providers:
            provider_name = provider.__class__.__name__
            self._log.info(f"Attempting to fetch weather data from {provider_name}...")
            data = provider.get_current_weather(lat, lon)
            if data:
                return data
            self._log.warning(f"Failed to get data from {provider_name}. Falling back to next provider.")
        return None

    def execute_main_cycle(self):
        self._log.info("Main cycle: Starting weather check.")
        current_location = self._get_current_location()

        if not current_location:
            self._log.error("Main cycle: Could not determine location, skipping.")
            return

        weather_data = self._get_weather_with_fallback(current_location['lat'], current_location['lon'])

        if weather_data:
            self._log.info(f"Main cycle: Successfully fetched weather data from '{weather_data.source}'.")
            for out in self._outputs:
                try:
                    out.output(weather_data)
                except Exception as e:
                    self._log.error(f"Main cycle: Failed to write to output {out.__class__.__name__}", exc_info=True)
        else:
            self._log.error("Main cycle: Failed to get weather data from all providers.")

    def execute_scheduled_cycle(self):
        if not self._scheduled_outputs:
            return

        self._log.info("Scheduled cycle: Starting weather check.")
        current_location = self._get_current_location()

        if not current_location:
            self._log.error("Scheduled cycle: Could not determine location, skipping.")
            return
            
        weather_data = self._get_weather_with_fallback(current_location['lat'], current_location['lon'])
        if weather_data:
            self._log.info(f"Scheduled cycle: Successfully fetched weather data from '{weather_data.source}'.")
            for out in self._scheduled_outputs:
                out.output(weather_data)
        else:
            self._log.error("Scheduled cycle: Failed to get weather data from all providers.")
            
    def close_outputs(self):
        self._log.info("Closing outputs for periodic service...")
        for out in self._outputs + self._scheduled_outputs:
            if hasattr(out, 'close') and callable(getattr(out, 'close')):
                out.close()