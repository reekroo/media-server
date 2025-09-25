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
        
    try:
        application = Application(logger=logger)
        application.run()

    except Exception as e:
        logger.critical(f"A critical error forced the service to stop: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()