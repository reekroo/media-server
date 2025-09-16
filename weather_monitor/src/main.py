import sys
import configs
from weather_logger import setup_logger
from app import Application

def main():
    logger = setup_logger('WeatherMonitor', configs.LOG_FILE_PATH)
    logger.info("Starting Weather Monitor service...")

    if not configs.OPENWEATHERMAP_API_KEY and not configs.WEATHERAPI_API_KEY:
        logger.critical("No weather API keys are configured. Service cannot start.")
        sys.exit(1)

    application = Application(logger=logger)
    application.run()

if __name__ == '__main__':
    main()