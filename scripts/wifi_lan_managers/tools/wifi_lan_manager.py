#!/usr/bin/env python3

import sys

sys.path.append('/home/reekroo/scripts')
from common.interface_monitor import InterfaceMonitor
from common.wifi_controller import WifiController
from common.logger import setup_logger

log = setup_logger('LanWifiPolicy', '/home/reekroo/scripts/logs/wifi_manager.log')

class LanWifiPolicy:
    def __init__(self, lan_interface_name='eth0'):
        self.lan_monitor = InterfaceMonitor(lan_interface_name)
        self.wifi_controller = WifiController()
        log.info("[LanWifiPolicy] LAN/Wi-Fi Policy Manager Initialized.")

    def apply(self):
        if not self.lan_monitor.is_up():
            log.info("[LanWifiPolicy] LAN connection not detected. No action needed.")
            return

        log.info(f"[LanWifiPolicy] LAN connection detected ({self.lan_monitor.interface_name} is UP).")

        if self.wifi_controller.is_blocked():
            log.info("[LanWifiPolicy] Wi-Fi is already disabled. No action needed.")
            return

        log.info("[LanWifiPolicy] Wi-Fi is active, applying block...")
        self.wifi_controller.set_blocked(True)

if __name__ == '__main__':
    try:
        policy = LanWifiPolicy()
        policy.apply()
        log.info("[LanWifiPolicy] Policy applied successfully.")
    except Exception as e:
        log.error(f"[LanWifiPolicy] Failed to apply LAN/Wi-Fi policy: {e}", exc_info=True)