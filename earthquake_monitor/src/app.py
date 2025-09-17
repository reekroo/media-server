import logging
import time
import configs

from utils.http_client import HttpClient
from data_sources.usgs_api import UsgsApiDataSource
from data_sources.emsc_api import EmscApiDataSource
from data_sources.isc_api import IscApiDataSource
from alerters.sound_alerter import SoundAlerter
from locations.socket_provider import SocketLocationProvider
from locations.config_provider import ConfigLocationProvider
from outputs.json_file_output import JsonFileOutput
from runners.periodic_task_runner import PeriodicTaskRunner
from services.realtime_monitor_service import RealtimeMonitorService
from services.historical_export_service import HistoricalExportService
from services.on_demand_earthquake_service import OnDemandEarthquakeService
from servers.on_demand_socket_server import OnDemandSocketServer

class Application:
    def __init__(self, logger: logging.Logger):
        self._logger = logger
        self._http_client = HttpClient()

        app_config = {
            'SEARCH_RADIUS_KM': configs.SEARCH_RADIUS_KM,
            'MIN_API_MAGNITUDE': configs.MIN_API_MAGNITUDE,
            'API_TIME_WINDOW_MINUTES': configs.API_TIME_WINDOW_MINUTES
        }
        self._data_sources = [
            UsgsApiDataSource(http_client=self._http_client, logger=self._logger, config=app_config),
            EmscApiDataSource(http_client=self._http_client, logger=self._logger, config=app_config),
            IscApiDataSource(http_client=self._http_client, logger=self._logger, config=app_config)
        ]
        self._location_providers = [
            SocketLocationProvider(logger=self._logger, socket_path=configs.LOCATION_SERVICE_SOCKET),
            ConfigLocationProvider(logger=self._logger, default_lat=configs.DEFAULT_LATITUDE, default_lon=configs.DEFAULT_LONGITUDE)
        ]

        self._realtime_service = self._create_realtime_service()
        self._historical_service = self._create_historical_service()
        self._on_demand_service = OnDemandEarthquakeService(data_sources=self._data_sources, logger=self._logger)

        self._realtime_runner = PeriodicTaskRunner(
            task_callable=self._realtime_service.execute_check,
            interval=configs.CHECK_INTERVAL_SECONDS,
            logger=self._logger,
            name="RealtimeMonitorRunner"
        )
        self._historical_runner = PeriodicTaskRunner(
            task_callable=self._historical_service.execute_export,
            interval=20 * 60,
            logger=self._logger,
            name="HistoricalExportRunner"
        )
        self._on_demand_server = OnDemandSocketServer(
            socket_path=configs.ON_DEMAND_EARTHQUAKE_SOCKET,
            service=self._on_demand_service,
            logger=self._logger
        )

        self._managed_components = [
            self._realtime_runner,
            self._historical_runner,
            self._on_demand_server
        ]

    def _create_realtime_service(self) -> RealtimeMonitorService:
        alerters = [SoundAlerter(logger=self._logger, socket_path=configs.BUZZER_SOCKET)]
        return RealtimeMonitorService(
            data_sources=self._data_sources,
            location_providers=self._location_providers,
            alerters=alerters,
            alert_levels_config=configs.ALERT_LEVELS,
            max_processed_events=configs.MAX_PROCESSED_EVENTS_MEMORY,
            logger=self._logger
        )

    def _create_historical_service(self) -> HistoricalExportService:
        json_output = JsonFileOutput(logger=self._logger)
        return HistoricalExportService(
            data_sources=self._data_sources,
            location_providers=self._location_providers,
            output=json_output,
            logger=self._logger,
            output_path='/run/monitors/earthquakes/last7d.json',
            fetch_days=7
        )

    def run(self):
        self._logger.info("Application starting all components...")
        
        try:
            self._historical_runner.start(run_immediately=True)
            self._realtime_runner.start()
            self._on_demand_server.start()
            
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