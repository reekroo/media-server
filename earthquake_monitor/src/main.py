import configs
import threading
from earthquake_logger import setup_logger
from earthquake_monitor import EarthquakeMonitor
from utils.http_client import HttpClient
from data_sources.usgs_api import UsgsApiDataSource
from data_sources.emsc_api import EmscApiDataSource
from data_sources.isc_api import IscApiDataSource
from alerters.sound_alerter import SoundAlerter
from locations.socket_provider import SocketLocationProvider
from locations.config_provider import ConfigLocationProvider
from historical_data_fetcher import HistoricalDataFetcher
from outputs.json_file_output import JsonFileOutput
from scheduler import DataExportScheduler

def main():
    main_logger = setup_logger('earthquake_monitor', configs.LOG_FILE_PATH)
    main_logger.info("Initializing Earthquake Monitor service...")
    
    http_client = HttpClient()

    app_config = {
        'SEARCH_RADIUS_KM': configs.SEARCH_RADIUS_KM,
        'MIN_API_MAGNITUDE': configs.MIN_API_MAGNITUDE,
        'API_TIME_WINDOW_MINUTES': configs.API_TIME_WINDOW_MINUTES
    }

    data_sources = [
        UsgsApiDataSource(http_client=http_client, logger=main_logger, config=app_config),
        EmscApiDataSource(http_client=http_client, logger=main_logger, config=app_config),
        IscApiDataSource(http_client=http_client, logger=main_logger, config=app_config)
    ]
    
    alerters = [
        SoundAlerter(logger=main_logger, socket_path=configs.BUZZER_SOCKET),
    ]

    location_providers = [
        SocketLocationProvider(
            logger=main_logger, 
            socket_path=configs.LOCATION_SERVICE_SOCKET
        ),
        ConfigLocationProvider(
            logger=main_logger,
            default_lat=configs.DEFAULT_LATITUDE,
            default_lon=configs.DEFAULT_LONGITUDE
        )
    ]

    main_logger.info("Initializing historical data export service...")
    json_output = JsonFileOutput(logger=main_logger)
    historical_fetcher = HistoricalDataFetcher(
        data_sources=data_sources,
        location_providers=location_providers,
        logger=main_logger
    )
    scheduler = DataExportScheduler(
        fetcher=historical_fetcher,
        output=json_output,
        logger=main_logger,
        output_path='/run/monitors/earthquakes/last7d.json',
        interval_minutes=20,
        fetch_days=7
    )
    scheduler_thread = scheduler.start(run_immediately=True)

    monitor = EarthquakeMonitor(
        data_sources=data_sources,
        location_providers=location_providers,
        alerters=alerters,
        alert_levels_config=configs.ALERT_LEVELS,
        max_processed_events=configs.MAX_PROCESSED_EVENTS_MEMORY,
        logger=main_logger
    )

    try:
        monitor.run(configs.CHECK_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        main_logger.info("Shutdown signal received. Stopping services...")
    finally:
        scheduler.stop()
        scheduler_thread.join()
        main_logger.info("Earthquake Monitor service has been shut down.")

if __name__ == "__main__":
    main()