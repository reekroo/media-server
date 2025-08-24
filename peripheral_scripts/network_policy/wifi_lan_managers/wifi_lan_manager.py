#!/usr/bin/env python3
from utils.interface_monitor import InterfaceMonitor
from utils.wifi_controller import WifiController
from utils.logger import setup_logger

from .configs import LOG_FILE, LAN_INTERFACE, AUTO_UNBLOCK_WHEN_LAN_DOWN

log = setup_logger('LanWifiPolicy', LOG_FILE)

class LanWifiPolicy:
    def __init__(self, lan_interface_name: str | None = None):
        name = lan_interface_name or LAN_INTERFACE
        self.lan_monitor = InterfaceMonitor(name, logger=log)
        self.wifi_controller = WifiController(logger=log)
        log.info("[LanWifiPolicy] Initialized (LAN=%s, auto-unblock=%s).", name, AUTO_UNBLOCK_WHEN_LAN_DOWN)

    def apply(self):
        if self.lan_monitor.is_up():
            log.info("[LanWifiPolicy] LAN is UP; ensuring Wi-Fi is blocked.")
            if self.wifi_controller.is_blocked():
                log.info("[LanWifiPolicy] Wi-Fi already blocked; nothing to do.")
                return
            if self.wifi_controller.set_blocked(True):
                log.info("[LanWifiPolicy] Wi-Fi blocked because LAN is up.")
            return

        # LAN is DOWN
        log.info("[LanWifiPolicy] LAN is DOWN.")
        if AUTO_UNBLOCK_WHEN_LAN_DOWN:
            if self.wifi_controller.is_blocked():
                log.info("[LanWifiPolicy] Auto-unblock policy active; unblocking Wi-Fi.")
                self.wifi_controller.set_blocked(False)
            else:
                log.info("[LanWifiPolicy] Wi-Fi already unblocked; nothing to do.")
        else:
            log.info("[LanWifiPolicy] Auto-unblock disabled; leaving Wi-Fi state as is.")
