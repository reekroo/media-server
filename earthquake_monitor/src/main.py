import asyncio
import configs
from earthquake_logger import setup_logger
from app import Application

async def async_main():
    """Основная асинхронная логика приложения."""
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
    """
    Синхронная точка входа для setuptools.
    Ее единственная задача - запустить асинхронную часть.
    """
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        # Этот блок нужен на случай, если пользователь прервет
        # программу до того, как основной try/except в async_main() начнет работать.
        print("\nApplication stopped during startup.")

# Этот блок теперь нужен только для прямого запуска файла (например, для отладки),
# но он будет работать правильно, вызывая синхронную main().
if __name__ == "__main__":
    main()