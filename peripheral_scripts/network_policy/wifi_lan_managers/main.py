#!/usr/bin/env python3
import sys

from . import configs
from .policy import LanWifiPolicy

from utils.logger import setup_logger
from utils.interface_monitor import InterfaceMonitor
from utils.wifi_controller import WifiController

def main():
    logger = setup_logger(
        logger_name='LanWifiPolicy',
        log_file=configs.LOG_FILE
    )

    try:
        lan_monitor = InterfaceMonitor(configs.LAN_INTERFACE, logger=logger)
        wifi_controller = WifiController(logger=logger)

        policy = LanWifiPolicy(
            lan_monitor=lan_monitor,
            wifi_controller=wifi_controller,
            auto_unblock=configs.AUTO_UNBLOCK_WHEN_LAN_DOWN,
            logger=logger
        )

        policy.apply()
        logger.info("Policy applied successfully.")

    except Exception:
        logger.critical("Critical error while applying LAN/Wi-Fi policy.", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()