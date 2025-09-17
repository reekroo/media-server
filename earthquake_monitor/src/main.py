import configs
from earthquake_logger import setup_logger
from app import Application

def main():
    logger = setup_logger('earthquake_monitor', configs.LOG_FILE_PATH)
    logger.info("Starting Earthquake Monitor service...")
    
    application = Application(logger=logger)
    application.run()

if __name__ == "__main__":
    main()