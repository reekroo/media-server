import sys
import configs
from location_logger import setup_logger
from app import Application

def main():
    log = setup_logger("LocationService", configs.LOG_FILE_PATH, configs.LOG_LEVEL)
    log.info("Starting Location Service...")

    try:
        application = Application(logger=log)
        application.run()
    except Exception as e:
        log.critical("A critical error forced the service to stop: %s", e, exc_info=True)
        sys.exit(1)
    
    log.info("Location Service has stopped.")

if __name__ == "__main__":
    main()