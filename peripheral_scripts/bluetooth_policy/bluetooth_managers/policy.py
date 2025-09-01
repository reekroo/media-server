import logging
from .strategies import RfkillBlock, BluetoothctlPowerOff, HciconfigDown

class BluetoothPolicy:
    def __init__(self, logger: logging.Logger, method: str, device: str):
        self._log = logger
        self._strategies = self._create_strategies(method, device)
        self._log.info("BluetoothPolicy init: primary_method=%s", method)

    def _create_strategies(self, method: str, device: str) -> list:
        all_strategies = {
            "rfkill": RfkillBlock(self._log),
            "bluetoothctl": BluetoothctlPowerOff(self._log),
            "hciconfig": HciconfigDown(self._log, device),
        }
        
        preferred = all_strategies.pop(method)
        fallbacks = list(all_strategies.values())
        
        return [preferred] + fallbacks

    def apply(self) -> None:
        self._log.info("Applying startup policy: force disable bluetooth.")
        
        for strategy in self._strategies:
            if strategy.execute():
                self._log.info("Bluetooth is OFF/blocked at boot.")
                return

        self._log.error("Failed to disable Bluetooth at boot (all methods failed).")