#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
from .ups_manager import UpsManager
from .configs import UPS_LOG_FILE

def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - UpsService - %(levelname)s - %(message)s',
        filename=UPS_LOG_FILE,
        filemode='a'
    )
    logging.getLogger().addHandler(logging.StreamHandler())
    logger = logging.getLogger(__name__)
    
    try:
        manager = UpsManager(logger)
        manager.loop()
    except KeyboardInterrupt:
        logger.info("Service stopped by user.")
    except Exception as e:
        logger.critical(f"Service failed to start or run: {e}", exc_info=True)

if __name__ == '__main__':
    main()