import sys
from pathlib import Path

import configs
from location_logger import setup_logger
from utils.http_client import HttpClient
from location_controller import LocationController
from providers.ipinfo_provider import IpInfoProvider
from providers.config_provider import ConfigFallbackProvider

def main():
    log = setup_logger("LocationService", configs.LOG_FILE_PATH, configs.LOG_LEVEL)
    log.info("Starting Location Service...")

    try:
        http_client = HttpClient()

        providers = [
            IpInfoProvider(http_client=http_client, logger=log),
            ConfigFallbackProvider(
                default_lat=configs.DEFAULT_LATITUDE,
                default_lon=configs.DEFAULT_LONGITUDE,
                logger=log
            )
        ]
        
        service = LocationController(
            providers=providers,
            logger=log,
            socket_path=Path(configs.LOCATION_SERVICE_SOCKET),
            update_interval=configs.UPDATE_INTERVAL_SECONDS
        )
        service.run()
    
    except Exception as e:
        log.critical("A critical error forced the service to stop: %s", e, exc_info=True)
        sys.exit(1)
    
    log.info("Location Service has stopped.")

if __name__ == "__main__":
    main()