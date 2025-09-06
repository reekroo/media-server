import time
import logging
import threading
from typing import List, Optional

from locations.base import ILocationProvider
from providers.base import IWeatherProvider
from outputs.base import IOutputStrategy
from models.weather_data import WeatherData

class WeatherController:
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
        
        self._stop_event = threading.Event()
        self._scheduler_thread = None
        
        self._log.info(
            f"WeatherController initialized with {len(weather_providers)} weather provider(s), "
            f"{len(location_providers)} location provider(s), {len(outputs)} main output(s), "
            f"and {len(self._scheduled_outputs)} scheduled output(s)."
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

    def _run_scheduler(self, interval_seconds: int):
        self._log.info(f"Scheduler thread for JSON output started with an interval of {interval_seconds} seconds.")
        
        while not self._stop_event.is_set():
            self._log.info("Starting new scheduled weather check cycle.")
            current_location = self._get_current_location()

            if not current_location:
                self._log.error("Scheduler: Could not determine location, skipping this cycle.")
            else:
                weather_data = self._get_weather_with_fallback(current_location['lat'], current_location['lon'])
                if weather_data:
                    self._log.info(f"Scheduler: Successfully fetched weather data from '{weather_data.source}'.")
                    for out in self._scheduled_outputs:
                        try:
                            out.output(weather_data)
                        except Exception:
                            self._log.error(f"Scheduler: Failed to write to output {out.__class__.__name__}", exc_info=True)
                else:
                    self._log.error("Scheduler: Failed to get weather data from all available providers.")
            
            self._log.info(f"Scheduler cycle finished. Waiting for {interval_seconds} seconds.")
            self._stop_event.wait(timeout=interval_seconds)
            
        self._log.info("Scheduler thread for JSON output has stopped.")

    def run(self, interval_seconds: int, scheduled_interval_seconds: Optional[int] = None):
        if self._scheduled_outputs and scheduled_interval_seconds is not None:
            self._scheduler_thread = threading.Thread(
                target=self._run_scheduler,
                args=(scheduled_interval_seconds,),
                name="WeatherJsonScheduler"
            )
            self._scheduler_thread.daemon = True
            self._scheduler_thread.start()
            
        self._log.info(f"Controller main loop started with a refresh interval of {interval_seconds} seconds.")
        
        try:
            while not self._stop_event.is_set():
                self._log.info("Starting new main weather check cycle.")
                current_location = self._get_current_location()

                if not current_location:
                    self._log.error("Main loop: Could not determine location, skipping this cycle.")
                    self._stop_event.wait(timeout=interval_seconds)
                    continue

                weather_data = self._get_weather_with_fallback(current_location['lat'], current_location['lon'])

                if weather_data:
                    self._log.info(f"Main loop: Successfully fetched weather data from '{weather_data.source}'.")
                    for out in self._outputs:
                        try:
                            out.output(weather_data)
                        except Exception:
                            self._log.error(f"Main loop: Failed to write to output {out.__class__.__name__}", exc_info=True)
                else:
                    self._log.error("Main loop: Failed to get weather data from all available providers.")

                self._log.info(f"Main loop cycle finished. Waiting for {interval_seconds} seconds.")
                self._stop_event.wait(timeout=interval_seconds)

        except KeyboardInterrupt:
            self._log.info("Keyboard interrupt received. Shutting down...")

        finally:
            self._log.info("Controller shutdown sequence initiated.")
            self._stop_event.set()
            
            if self._scheduler_thread and self._scheduler_thread.is_alive():
                self._log.info("Waiting for scheduler thread to finish...")
                self._scheduler_thread.join(timeout=5.0)

            for out in self._outputs + self._scheduled_outputs:
                try:
                    if hasattr(out, 'close') and callable(getattr(out, 'close')):
                        out.close()
                except Exception:
                    self._log.error(f"Error while closing output {out.__class__.__name__}", exc_info=True)
            self._log.info("Controller has been shut down.")