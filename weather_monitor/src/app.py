import logging
import time

from configs import (
    OPENWEATHERMAP_API_KEY, WEATHERAPI_API_KEY, ON_DEMAND_WEATHER_SOCKET,
    LOCATION_SERVICE_SOCKET, DEFAULT_LATITUDE, DEFAULT_LONGITUDE,
    WEATHER_SERVICE_SOCKET, WEATHER_JSON_FILE_PATH, INTERVAL_SECONDS,
    JSON_INTERVAL_SECONDS
)
from utils.http_client import HttpClient
from providers.openweathermap import OpenWeatherMapProvider
from providers.weatherapi import WeatherApiProvider
from services.periodic_weather_service import PeriodicWeatherService
from services.on_demand_weather_service import OnDemandWeatherService
from servers.on_demand_socket import OnDemandSocketServer
from runners.periodic_task_runner import PeriodicTaskRunner
from outputs.console_output import ConsoleOutput
from outputs.socket_output import SocketOutput
from outputs.file_output import FileOutput
from locations.config_provider import ConfigLocationProvider
from locations.socket_provider import SocketLocationProvider

class Application:
    def __init__(self, logger: logging.Logger):
        self._logger = logger
        self._http_client = HttpClient()
        
        self._weather_providers = [
            OpenWeatherMapProvider(
                api_key=OPENWEATHERMAP_API_KEY, http_client=self._http_client, logger=self._logger
            ),
            WeatherApiProvider(
                api_key=WEATHERAPI_API_KEY, http_client=self._http_client, logger=self._logger
            )
        ]
        
        self._on_demand_service = OnDemandWeatherService(
            weather_providers=self._weather_providers, logger=self._logger
        )
        self._periodic_service = self._create_periodic_service()

        self._main_task_runner = PeriodicTaskRunner(
            task_callable=self._periodic_service.execute_main_cycle,
            interval=INTERVAL_SECONDS,
            logger=self._logger,
            name="MainCycleRunner"
        )
        
        self._scheduled_task_runner = PeriodicTaskRunner(
            task_callable=self._periodic_service.execute_scheduled_cycle,
            interval=JSON_INTERVAL_SECONDS,
            logger=self._logger,
            name="ScheduledCycleRunner"
        )

        self._on_demand_server = OnDemandSocketServer(
            socket_path=ON_DEMAND_WEATHER_SOCKET,
            on_demand_service=self._on_demand_service,
            logger=self._logger
        )

        self._managed_components = [
            self._main_task_runner,
            self._scheduled_task_runner,
            self._on_demand_server
        ]

    def _create_periodic_service(self) -> PeriodicWeatherService:
        location_providers = [
            SocketLocationProvider(socket_path=LOCATION_SERVICE_SOCKET, logger=self._logger),
            ConfigLocationProvider(lat=DEFAULT_LATITUDE, lon=DEFAULT_LONGITUDE, logger=self._logger)
        ]
        outputs = [
            ConsoleOutput(logger=self._logger),
            SocketOutput(socket_path=WEATHER_SERVICE_SOCKET, logger=self._logger)
        ]
        scheduled_outputs = [
            FileOutput(file_path=WEATHER_JSON_FILE_PATH, logger=self._logger)
        ]
        return PeriodicWeatherService(
            weather_providers=self._weather_providers,
            outputs=outputs,
            location_providers=location_providers,
            logger=self._logger,
            scheduled_outputs=scheduled_outputs
        )

    def run(self):
        self._logger.info("Application starting all components...")
        
        try:
            for component in self._managed_components:
                component.start()

            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self._logger.info("Shutdown signal received.")
        finally:
            self.close()

    def close(self):
        self._logger.info("Application shutdown sequence initiated.")
        
        for component in reversed(self._managed_components):
            try:
                if hasattr(component, 'stop'):
                    component.stop()
                elif hasattr(component, 'close'):
                    component.close()
            except Exception as e:
                self._logger.error(f"Error stopping component {component.__class__.__name__}: {e}")
        
        self._periodic_service.close_outputs()
        self._logger.info("Application has been shut down.")