import asyncio
import configs
from earthquake_logger import setup_logger
from app import Application

async def async_main():
    logger = setup_logger('earthquake_monitor', configs.LOG_FILE_PATH)
    logger.info("Starting Earthquake Monitor service...")
    
    application = Application(logger=logger)
    
    try:
        await application.run()
    except (KeyboardInterrupt, asyncio.CancelledError):
        logger.info("Shutdown signal received.")
    finally:
        logger.info("Initiating graceful shutdown...")
        await application.close()

def main():
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("\nApplication stopped during startup.")

if __name__ == "__main__":
    main()