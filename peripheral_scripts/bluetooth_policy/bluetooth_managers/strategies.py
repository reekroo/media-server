from abc import ABC, abstractmethod
import subprocess
import logging

class ShutdownStrategy(ABC):
    def __init__(self, logger: logging.Logger):
        self._log = logger

    @abstractmethod
    def execute(self) -> bool:
        ...

    def _run(self, cmd: list[str]) -> tuple[int, str, str]:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        out, err = proc.communicate()
        return proc.returncode, out.strip(), err.strip()

class RfkillBlock(ShutdownStrategy):
    def execute(self) -> bool:
        code, _, err = self._run(["/usr/sbin/rfkill", "block", "bluetooth"])
        if code == 0:
            self._log.info("Strategy 'rfkill': bluetooth blocked.")
            return True
        self._log.error("Strategy 'rfkill' failed (%s): %s", code, err)
        return False

class BluetoothctlPowerOff(ShutdownStrategy):
    def execute(self) -> bool:
        code, _, err = self._run(["/usr/bin/bluetoothctl", "power", "off"])
        if code == 0:
            self._log.info("Strategy 'bluetoothctl': power off OK.")
            return True
        self._log.error("Strategy 'bluetoothctl' failed (%s): %s", code, err)
        return False

class HciconfigDown(ShutdownStrategy):
    def __init__(self, logger: logging.Logger, device: str):
        super().__init__(logger)
        self._device = device

    def execute(self) -> bool:
        code, _, err = self._run(["/usr/bin/hciconfig", self._device, "down"])
        if code == 0:
            self._log.info("Strategy 'hciconfig': %s down.", self._device)
            return True
        self._log.error("Strategy 'hciconfig' failed (%s): %s", code, err)
        return False