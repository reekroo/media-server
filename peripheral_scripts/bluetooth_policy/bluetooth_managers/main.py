#!/usr/bin/env python3
from . import configs
from .policy import BluetoothPolicy
from utils.logger import setup_logger

def main():
    logger = setup_logger(
        logger_name="BluetoothPolicy", 
        log_file=configs.LOG_FILE
    )
    
    try:
        policy = BluetoothPolicy(
            logger=logger, 
            method=configs.BT_BLOCK_METHOD, 
            device=configs.BT_DEVICE
        )
        policy.apply()
        logger.info("Policy applied successfully.")
    except Exception as e:
        logger.error(f"Failed to apply policy: {e}", exc_info=True)

if __name__ == "__main__":
    main()