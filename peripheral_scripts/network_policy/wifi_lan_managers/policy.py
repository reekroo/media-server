import logging
from utils.interface_monitor import InterfaceMonitor
from utils.wifi_controller import WifiController

class LanWifiPolicy:
    def __init__(
        self,
        lan_monitor: InterfaceMonitor,
        wifi_controller: WifiController,
        auto_unblock: bool,
        logger: logging.Logger
    ):
        self._lan_monitor = lan_monitor
        self._wifi_controller = wifi_controller
        self._auto_unblock = auto_unblock
        self._log = logger
        self._log.info(
            "LanWifiPolicy initialized (LAN=%s, auto-unblock=%s).",
            lan_monitor.interface_name, auto_unblock
        )

    def apply(self) -> None:
        if self._lan_monitor.is_up():
            self._handle_lan_up()
        else:
            self._handle_lan_down()

    def _handle_lan_up(self):
        self._log.info("LAN is UP. Ensuring Wi-Fi is blocked.")
        if self._wifi_controller.is_blocked():
            self._log.info("Wi-Fi is already blocked, no action needed.")
            return

        if self._wifi_controller.set_blocked(True):
            self._log.info("Wi-Fi was successfully blocked.")
        else:
            self._log.error("Failed to block Wi-Fi.")

    def _handle_lan_down(self):
        self._log.info("LAN is DOWN.")
        if not self._auto_unblock:
            self._log.info("Auto-unblock is disabled; leaving Wi-Fi state as is.")
            return

        self._log.info("Auto-unblock policy is active. Ensuring Wi-Fi is unblocked.")
        if not self._wifi_controller.is_blocked():
            self._log.info("Wi-Fi is already unblocked, no action needed.")
            return

        if self._wifi_controller.set_blocked(False):
            self._log.info("Wi-Fi was successfully unblocked.")
        else:
            self._log.error("Failed to unblock Wi-Fi.")