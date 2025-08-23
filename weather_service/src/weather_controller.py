import time
from typing import List
from providers.base import IWeatherProvider
from outputs.base import IOutputStrategy
from weather_logger import get_logger

log = get_logger(__name__)

class WeatherController:
    def __init__(self, providers: List[IWeatherProvider], outputs: List[IOutputStrategy], lat: float, lon: float):
        self._providers = providers
        self._outputs = outputs
        self._lat = lat
        self._lon = lon
        log.info(f"WeatherController initialized for coords: ({self._lat}, {self._lon})")

    def _get_weather_with_fallback(self):
        for provider in self._providers:
            provider_name = provider.__class__.__name__
            
            log.info(f"Attempting to fetch data from {provider_name}")
            
            data = provider.get_current_weather(self._lat, self._lon)
            
            if data:
                return data
        
            log.warning(f"Failed to get data from {provider_name}. Falling back.")

        return None

    def run(self, interval_seconds: int):
        log.info(f"Controller started with interval {interval_seconds} seconds.")
        
        try:
            while True:
                log.info("Starting new weather check cycle.")
                weather_data = self._get_weather_with_fallback()
                
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