import time
import subprocess
from dataclasses import dataclass
from typing import Optional, Tuple
import logging

from .providers.ups_reading_interface import UpsReading

@dataclass
class ShutdownConfig:
    low_battery_percent: float
    critical_voltage_v: float
    debounce_sec: float
    shutdown_cmd: Tuple[str, ...]
    dry_run: bool

class ShutdownPolicy:
    def __init__(self, config: ShutdownConfig, logger: logging.Logger):
        self._config = config
        self._log = logger
        self._shutdown_fired = False
        self._low_batt_since: Optional[float] = None

    def check(self, reading: UpsReading) -> None:
        if self._shutdown_fired or reading.ac_present:
            if self._low_batt_since is not None:
                self._log.info("AC power restored or condition cleared. Cancelling shutdown timer.")
                self._low_batt_since = None
            return

        is_low_voltage = (0.5 < reading.voltage_v <= self._config.critical_voltage_v)
        is_low_soc = (reading.soc_percent <= self._config.low_battery_percent)
        
        should_trigger = is_low_voltage or is_low_soc
        
        if not should_trigger:
            self._low_batt_since = None
            return

        if self._low_batt_since is None:
            self._low_batt_since = time.time()
            reason = "Voltage" if is_low_voltage else "SOC"
            self._log.warning(
                f"CRITICAL {reason} DETECTED (U={reading.voltage_v:.3f}V, SOC={reading.soc_percent:.1f}%). Starting shutdown timer..."
            )
        
        if time.time() - self._low_batt_since >= self._config.debounce_sec:
            self._shutdown_fired = True
            msg = f"Shutting down (U={reading.voltage_v:.3f}V, SOC={reading.soc_percent:.1f}%)"
            
            if self._config.dry_run:
                self._log.warning(f"DRY_RUN: {msg}")
            else:
                self._log.error(msg)
                try:
                    subprocess.Popen(self._config.shutdown_cmd)
                except Exception as e:
                    self._log.exception(f"Failed to call shutdown command: {e}")