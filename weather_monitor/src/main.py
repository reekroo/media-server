#!/usr/bin/env python3
import sys

import configs
from weather_logger import setup_logger
from utils.http_client import HttpClient
from providers.openweathermap import OpenWeatherMapProvider
from providers.weatherapi import WeatherApiProvider
from outputs.console_output import ConsoleOutput
from outputs.socket_output import SocketOutput
from locations.config_provider import ConfigLocationProvider
from locations.socket_provider import SocketLocationProvider
from weather_controller import WeatherController

def main():
    logger = setup_logger('WeatherMonitor', configs.LOG_FILE_PATH)
    logger.info("Starting Weather Monitor service...")

    if not configs.OPENWEATHERMAP_API_KEY and not configs.WEATHERAPI_API_KEY:
        logger.critical("No weather API keys are configured. Service cannot start.")
        sys.exit(1)

    try:
        http_client = HttpClient()

        location_providers = [
            SocketLocationProvider(
                socket_path=configs.LOCATION_SERVICE_SOCKET,
                logger=logger
            ),
            ConfigLocationProvider(
                lat=configs.DEFAULT_LATITUDE,
                lon=configs.DEFAULT_LONGITUDE,
                logger=logger
            )
        ]

        weather_providers = [
            OpenWeatherMapProvider(
                api_key=configs.OPENWEATHERMAP_API_KEY,
                http_client=http_client,
                logger=logger
            ),
            WeatherApiProvider(
                api_key=configs.WEATHERAPI_API_KEY,
                http_client=http_client,
                logger=logger
            )
        ]

        outputs = [
            ConsoleOutput(logger=logger),
            SocketOutput(socket_path=configs.WEATHER_SERVICE_SOCKET, logger=logger)
        ]

        controller = WeatherController(
            weather_providers=weather_providers,
            outputs=outputs,
            location_providers=location_providers,
            logger=logger
        )

        controller.run(interval_seconds=configs.INTERVAL_SECONDS)

    except KeyboardInterrupt:
        logger.info("Service stopped by user.")
    except Exception:
        logger.critical("A fatal error occurred, service is shutting down.", exc_info=True)
        sys.exit(1)

    logger.info("Weather Monitor service has shut down.")

if __name__ == '__main__':
    main()