#!/usr/bin/env python3
import os, json, time, subprocess
from typing import Optional
import smbus2, RPi.GPIO as GPIO

from .configs import (
    I2C_BUS, I2C_ADDR, GPIO_AC_PIN, AC_ACTIVE_HIGH,
    POLL_INTERVAL_SEC, LOW_BATTERY_PERCENT, LOW_BATT_DEBOUNCE_SEC,
    CRITICAL_VOLTAGE_V, VOLTAGE_MIN, VOLTAGE_MAX,
    UPS_STATE_DIR, UPS_STATUS_PATH, DRY_RUN, SHUTDOWN_CMD,
)

class UpsManager:
    def __init__(self, logger):
        self.log = logger
        self.bus = smbus2.SMBus(I2C_BUS)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(GPIO_AC_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN if AC_ACTIVE_HIGH else GPIO.PUD_UP)
        os.makedirs(UPS_STATE_DIR, exist_ok=True)
        self._shutdown_fired = False
        self._low_batt_since: Optional[float] = None
        self._last_display_soc = 101.0
        
        self.log.info(f"UPS started. Shutdown on SOC <= {LOW_BATTERY_PERCENT}% OR Voltage <= {CRITICAL_VOLTAGE_V}V")

    def _read_word_robustly(self, reg: int) -> Optional[int]:
        for _ in range(3):
            try:
                data = self.bus.read_i2c_block_data(I2C_ADDR, reg, 2)
                return (data[0] << 8) | data[1]
            except IOError: time.sleep(0.1)
        return None

    def _read_soc(self) -> float:
        raw = self._read_word_robustly(0x04)
        if raw is None: 
            return 0.0
        return max(0.0, min(100.0, raw / 256.0))

    def _read_voltage(self) -> float:
        raw = self._read_word_robustly(0x02)
        if raw is None: 
            return 0.0
        return (raw * 78.125) / 1_000_000.0

    def _calculate_display_soc(self, voltage: float) -> float:
        voltage = max(VOLTAGE_MIN, min(VOLTAGE_MAX, voltage))
        percentage = ((voltage - VOLTAGE_MIN) / (VOLTAGE_MAX - VOLTAGE_MIN)) * 100
        return percentage

    def _write_status(self, ac, soc_chip, volt, soc_display_filtered):
        payload = {
            "ts": time.time(),
            "ac_present": bool(ac),
            "voltage_v": float(round(volt, 3)),
            "soc_chip_percent": float(round(soc_chip, 2)),
            "soc_display_percent": float(round(soc_display_filtered, 2)),
        }
        tmp_path = UPS_STATUS_PATH + ".tmp"
        with open(tmp_path, "w") as f: json.dump(payload, f, separators=(",", ":"))
        os.replace(tmp_path, UPS_STATUS_PATH)

    def _maybe_shutdown(self, ac_present: bool, soc_percent: float, voltage_v: float) -> None:
        if self._shutdown_fired or ac_present:
            if self._low_batt_since is not None: self.log.info("Cancelling shutdown timer."); self._low_batt_since = None
            return
        
        is_low_voltage = (0.5 < voltage_v <= CRITICAL_VOLTAGE_V)
        is_low_soc = (soc_percent <= LOW_BATTERY_PERCENT)
        
        if is_low_voltage or is_low_soc:
            if self._low_batt_since is None:
                self._low_batt_since = time.time()
                reason = "Voltage" if is_low_voltage else "SOC"
                self.log.warning(f"CRITICAL {reason} DETECTED (U={voltage_v:.3f}V, SOC={soc_percent:.1f}%). Starting timer...")
            if time.time() - self._low_batt_since >= LOW_BATT_DEBOUNCE_SEC:
                self._shutdown_fired = True
                msg = f"Shutting down (U={voltage_v:.3f}V, SOC={soc_percent:.1f}%)"
                if DRY_RUN: self.log.warning(f"DRY_RUN: {msg}")
                else:
                    self.log.error(msg)
                    try: subprocess.Popen(SHUTDOWN_CMD)
                    except Exception as e: self.log.exception(f"Failed to call shutdown: {e}")
        else:
            self._low_batt_since = None

    def loop(self) -> None:
        try:
            while True:
                try:
                    volt = self._read_voltage()
                    soc_chip = self._read_soc()
                    ac = GPIO.input(GPIO_AC_PIN) == (GPIO.HIGH if AC_ACTIVE_HIGH else GPIO.LOW)
                    
                    if volt > 0.1 or soc_chip > 0.1:
                        soc_display_raw = self._calculate_display_soc(volt)
                        
                        if not ac and soc_display_raw < self._last_display_soc:
                            self._last_display_soc = soc_display_raw
                        elif ac:
                             self._last_display_soc = soc_display_raw
                        
                        soc_display_filtered = self._last_display_soc
                        
                        self._write_status(ac, soc_chip, volt, soc_display_filtered)
                        self.log.info(f"AC={ac} SOC_chip={soc_chip:.1f}% SOC_display={soc_display_filtered:.1f}% U={volt:.3f}V")
                        self._maybe_shutdown(ac, soc_chip, volt)

                except Exception as e:
                    self.log.exception(f"Loop error: {e}")
                time.sleep(POLL_INTERVAL_SEC)
        finally:
            GPIO.cleanup()