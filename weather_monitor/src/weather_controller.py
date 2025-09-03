import time
import logging
from typing import List

from locations.base import ILocationProvider
from providers.base import IWeatherProvider
from outputs.base import IOutputStrategy
from models.weather_data import WeatherData

class WeatherController:
    def __init__(self,
                 weather_providers: List[IWeatherProvider],
                 outputs: List[IOutputStrategy],
                 location_providers: List[ILocationProvider],
                 logger: logging.Logger):
        self._providers = weather_providers
        self._outputs = outputs
        self._location_providers = location_providers
        self._log = logger
        self._log.info(
            f"WeatherController initialized with {len(weather_providers)} weather provider(s), "
            f"{len(location_providers)} location provider(s), and {len(outputs)} output(s)."
        )

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

    def run(self, interval_seconds: int):
        self._log.info(f"Controller started with a refresh interval of {interval_seconds} seconds.")

        try:
            while True:
                self._log.info("Starting new weather check cycle.")
                current_location = self._get_current_location()

                if not current_location:
                    self._log.error("Could not determine location, skipping weather check for this cycle.")
                    time.sleep(interval_seconds)
                    continue

                weather_data = self._get_weather_with_fallback(current_location['lat'], current_location['lon'])

                if weather_data:
                    self._log.info(f"Successfully fetched weather data from '{weather_data.source}'.")
                    for out in self._outputs:
                        try:
                            out.output(weather_data)
                        except Exception:
                            self._log.error(f"Failed to write to output {out.__class__.__name__}", exc_info=True)
                else:
                    self._log.error("Failed to get weather data from all available providers.")

                self._log.info(f"Cycle finished. Waiting for {interval_seconds} seconds.")
                time.sleep(interval_seconds)

        except KeyboardInterrupt:
            self._log.info("Keyboard interrupt received. Shutting down...")

        finally:
            for out in self._outputs:
                try:
                    out.close()
                except Exception:
                    self._log.error(f"Error while closing output {out.__class__.__name__}", exc_info=True)
            self._log.info("Controller has been shut down.")