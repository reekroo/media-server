import os, json, time, subprocess
import smbus2, RPi.GPIO as GPIO

from .configs import (
    I2C_BUS, I2C_ADDR,
    GPIO_AC_PIN, AC_ACTIVE_HIGH,
    POLL_INTERVAL_SEC, LOW_BATTERY_PERCENT, LOW_BATT_DEBOUNCE_SEC,
    UPS_STATE_DIR, UPS_STATUS_PATH,
    DRY_RUN, SHUTDOWN_CMD,
)

def _read_word_swapped(bus, addr, reg):
    val = bus.read_word_data(addr, reg)
    lo = val & 0xFF
    hi = (val >> 8) & 0xFF
    return (hi << 8) | lo

class UpsManager:
    def __init__(self, logger):
        self.log = logger
        self.bus = smbus2.SMBus(I2C_BUS)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(
            GPIO_AC_PIN,
            GPIO.IN,
            pull_up_down=GPIO.PUD_DOWN if AC_ACTIVE_HIGH else GPIO.PUD_UP
        )
        os.makedirs(UPS_STATE_DIR, exist_ok=True)
        self._shutdown_fired = False
        self._low_batt_since = None

    def _read_soc(self):
        raw = _read_word_swapped(self.bus, I2C_ADDR, 0x04)
        return max(0.0, min(100.0, raw / 256.0))

    def _read_voltage(self):
        raw = _read_word_swapped(self.bus, I2C_ADDR, 0x02)
        return (raw * 78.125) / 1_000_000.0

    def _is_ac(self):
        level = GPIO.input(GPIO_AC_PIN)
        return (level == GPIO.HIGH) if AC_ACTIVE_HIGH else (level == GPIO.LOW)

    def _write_status(self, ac, soc, volt):
        status = {
            "ts": int(time.time()),
            "ac_present": ac,
            "charging": ac and (soc < 100.0),
            "soc_percent": round(soc, 2),
            "voltage_v": round(volt, 3),
        }
        with open(UPS_STATUS_PATH, "w") as f:
            json.dump(status, f)

    def _maybe_shutdown(self, ac, soc):
        if ac or soc > LOW_BATTERY_PERCENT:
            self._low_batt_since = None
            return
        now = time.time()
        if self._low_batt_since is None:
            self._low_batt_since = now
            return
        if (now - self._low_batt_since) >= LOW_BATT_DEBOUNCE_SEC and not self._shutdown_fired:
            self._shutdown_fired = True
            msg = f"Battery {soc:.1f}% <= {LOW_BATTERY_PERCENT}%, AC=OFF → shutdown"
            self.log.error(msg)
            if DRY_RUN:
                self.log.warning("DRY RUN enabled, skipping shutdown")
            else:
                try:
                    subprocess.Popen(SHUTDOWN_CMD)
                except Exception as e:
                    self.log.exception("Failed to execute shutdown: %s", e)

    def loop(self):
        self.log.info("UPS started (i2c=%d, addr=0x%02X, ac_pin=BCM%d)",
                      I2C_BUS, I2C_ADDR, GPIO_AC_PIN)
        try:
            while True:
                try:
                    ac = self._is_ac()
                    soc = self._read_soc()
                    volt = self._read_voltage()
                    self._write_status(ac, soc, volt)
                    self.log.info("AC=%s SOC=%.2f%% U=%.3fV", ac, soc, volt)
                    self._maybe_shutdown(ac, soc)
                except Exception as e:
                    self.log.exception("loop error: %s", e)
                time.sleep(POLL_INTERVAL_SEC)
        finally:
            try:
                self.bus.close()
            finally:
                GPIO.cleanup()
