#!/usr/bin/env python3
import subprocess
from .configs import LOG_FILE, BT_BLOCK_METHOD, BT_DEVICE
from utils.logger import setup_logger

log = setup_logger("BluetoothPolicy", LOG_FILE)

class BluetoothPolicy:
    def __init__(self):
        log.info("[BluetoothPolicy] init: method=%s device=%s", BT_BLOCK_METHOD, BT_DEVICE)

    def _run(self, cmd: list[str]) -> tuple[int, str, str]:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        out, err = proc.communicate()
        return proc.returncode, out.strip(), err.strip()

    def _rfkill_block(self) -> bool:
        code, out, err = self._run(["/usr/sbin/rfkill", "block", "bluetooth"])
        if code == 0:
            log.info("[BluetoothPolicy] rfkill: bluetooth blocked.")
            return True
        log.error("[BluetoothPolicy] rfkill failed (%s): %s", code, err)
        return False

    def _bluetoothctl_power_off(self) -> bool:
        code, out, err = self._run(["/usr/bin/bluetoothctl", "power", "off"])
        if code == 0:
            log.info("[BluetoothPolicy] bluetoothctl: power off OK.")
            return True
        log.error("[BluetoothPolicy] bluetoothctl failed (%s): %s", code, err)
        return False

    def _hciconfig_down(self) -> bool:
        code, out, err = self._run(["/usr/bin/hciconfig", BT_DEVICE, "down"])
        if code == 0:
            log.info("[BluetoothPolicy] hciconfig: %s down.", BT_DEVICE)
            return True
        log.error("[BluetoothPolicy] hciconfig failed (%s): %s", code, err)
        return False

    def apply(self) -> None:
        log.info("[BluetoothPolicy] Applying startup policy: force disable bluetooth.")
        ok = False
        if BT_BLOCK_METHOD == "rfkill":
            ok = self._rfkill_block()
            if not ok:
                # fallback
                ok = self._bluetoothctl_power_off() or self._hciconfig_down()
        elif BT_BLOCK_METHOD == "bluetoothctl":
            ok = self._bluetoothctl_power_off()
            if not ok:
                ok = self._rfkill_block() or self._hciconfig_down()
        else:  # hciconfig
            ok = self._hciconfig_down()
            if not ok:
                ok = self._rfkill_block() or self._bluetoothctl_power_off()

        if ok:
            log.info("[BluetoothPolicy] Bluetooth is OFF/blocked at boot.")
        else:
            log.error("[BluetoothPolicy] Failed to disable Bluetooth at boot (all methods).")
