import time
from typing import List
from locations.base import ILocationProvider
from providers.base import IWeatherProvider
from outputs.base import IOutputStrategy
from weather_logger import get_logger

log = get_logger(__name__)

class WeatherController:
    def __init__(self, weather_providers: List[IWeatherProvider], outputs: List[IOutputStrategy], location_providers: List[ILocationProvider]):
        self._providers = weather_providers
        self._outputs = outputs
        self._location_providers = location_providers
        log.info(f"WeatherController initialized.")

    def _get_current_location(self) -> dict | None:
        for provider in self._location_providers:
            location = provider.get_location()
            if location:
                return location
        log.error("Failed to get location from all available providers.")
        return None

    def _get_weather_with_fallback(self, lat: float, lon: float):
        for provider in self._providers:
            provider_name = provider.__class__.__name__            
            log.info(f"Attempting to fetch data from {provider_name}")
            
            data = provider.get_current_weather(lat, lon)
            if data:
                return data        
        log.warning(f"Failed to get data from {provider_name}. Falling back.")
        return None

    def run(self, interval_seconds: int):
        log.info(f"Controller started with interval {interval_seconds} seconds.")
        
        try:
            while True:
                log.info("Starting new weather check cycle.")
                current_location = self._get_current_location()
                
                if not current_location:
                    log.error("Could not determine location, skipping weather check.")
                    time.sleep(interval_seconds)
                    continue
                
                weather_data = self._get_weather_with_fallback(current_location['lat'], current_location['lon'])
                
                if weather_data:
                    for out in self._outputs:
                        try:
                            out.output(weather_data)
                        except Exception as e:
                            log.error(f"Failed to write to output {out.__class__.__name__}: {e}")
                else:
                    log.error("Failed to get data from all available providers.")
                
                log.info(f"Cycle finished. Waiting for {interval_seconds} seconds.")
                time.sleep(interval_seconds)

        except KeyboardInterrupt:
            log.info("Keyboard interrupt received. Shutting down.")

        finally:
            for out in self._outputs:
                out.close()
            log.info("Controller has been shut down.")