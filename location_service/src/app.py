import logging
import time
from pathlib import Path

import configs
from utils.http_client import HttpClient
from providers.ipinfo_provider import IpInfoProvider
from providers.config_provider import ConfigFallbackProvider
from providers.nominatim_provider import NominatimProvider
from services.ip_location_service import IpLocationService
from services.geocoding_service import GeocodingService
from runners.periodic_task_runner import PeriodicTaskRunner
from servers.push_server import PushServer
from servers.on_demand_server import OnDemandGeocodingServer

class Application:
    def __init__(self, logger: logging.Logger):
        self._logger = logger
        self._http_client = HttpClient()

        self._ip_location_service = self._create_ip_location_service()
        self._geocoding_service = self._create_geocoding_service()

        self._ip_update_runner = PeriodicTaskRunner(
            task_callable=self._ip_location_service.update_location,
            interval=configs.UPDATE_INTERVAL_SECONDS,
            logger=self._logger,
            name="IpLocationUpdateRunner"
        )
        self._push_server = PushServer(
            service=self._ip_location_service,
            logger=self._logger,
            socket_path=Path(configs.LOCATION_SERVICE_SOCKET)
        )
        self._geocoding_server = OnDemandGeocodingServer(
            service=self._geocoding_service,
            logger=self._logger,
            socket_path=Path(configs.ON_DEMAND_GEOCODING_SOCKET)
        )

        self._managed_components = [
            self._ip_update_runner,
            self._push_server,
            self._geocoding_server
        ]

    def _create_ip_location_service(self) -> IpLocationService:
        providers = [
            IpInfoProvider(http_client=self._http_client, logger=self._logger),
            ConfigFallbackProvider(
                default_lat=configs.DEFAULT_LATITUDE,
                default_lon=configs.DEFAULT_LONGITUDE,
                logger=self._logger
            )
        ]
        return IpLocationService(providers=providers, logger=self._logger)

    def _create_geocoding_service(self) -> GeocodingService:
        provider = NominatimProvider(http_client=self._http_client, logger=self._logger)
        return GeocodingService(provider=provider, logger=self._logger)

    def run(self):
        self._logger.info("Application starting all components...")
        try:
            self._ip_update_runner.start(run_immediately=True)
            self._push_server.start()
            self._geocoding_server.start()

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
            except Exception as e:
                self._logger.error(f"Error stopping component {component.__class__.__name__}: {e}")
        self._logger.info("Application has been shut down.")