#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json
import time
import subprocess
from typing import Optional

import smbus2
import RPi.GPIO as GPIO

from .configs import (
    I2C_BUS, I2C_ADDR,
    GPIO_AC_PIN, AC_ACTIVE_HIGH,
    POLL_INTERVAL_SEC, LOW_BATTERY_PERCENT, LOW_BATT_DEBOUNCE_SEC,
    UPS_STATE_DIR, UPS_STATUS_PATH,
    DRY_RUN, SHUTDOWN_CMD,
)


class UpsManager:
    """
    Главный цикл опроса ИБП с улучшенной стабильностью чтения данных.
    """

    def __init__(self, logger):
        self.log = logger
        self.bus = smbus2.SMBus(I2C_BUS)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(
            GPIO_AC_PIN,
            GPIO.IN,
            pull_up_down=GPIO.PUD_DOWN if AC_ACTIVE_HIGH else GPIO.PUD_UP,
        )
        os.makedirs(UPS_STATE_DIR, exist_ok=True)
        self._shutdown_fired = False
        self._low_batt_since: Optional[float] = None
        self.log.info(
            "UPS started (i2c=%s, addr=0x%02X, ac_pin=BCM%d)",
            I2C_BUS, I2C_ADDR, GPIO_AC_PIN
        )

    def _read_word_robustly(self, reg: int) -> Optional[int]:
        """ Читает слово из регистра с 3 попытками в случае ошибки. """
        for i in range(3):
            try:
                data = self.bus.read_i2c_block_data(I2C_ADDR, reg, 2)
                return (data[0] << 8) | data[1]  # MSB << 8 | LSB
            except IOError as e:
                self.log.warning("I2C read error on attempt %d/%d: %s", i + 1, 3, e)
                time.sleep(0.1) # Короткая пауза перед повторной попыткой
        return None

    def _read_soc(self) -> float:
        """ Читает SOC, возвращает 0.0 если чтение не удалось. """
        raw = self._read_word_robustly(0x04)
        if raw is None:
            self.log.error("Failed to read SOC after 3 attempts.")
            return 0.0 # Возвращаем безопасное значение
        soc = raw / 256.0
        return max(0.0, min(100.0, soc))

    def _read_voltage(self) -> float:
        """ Читает напряжение, возвращает 0.0 если чтение не удалось. """
        raw = self._read_word_robustly(0x02)
        if raw is None:
            self.log.error("Failed to read Voltage after 3 attempts.")
            return 0.0 # Возвращаем безопасное значение
        return (raw * 78.125) / 1_000_000.0

    def _is_ac(self) -> bool:
        level = GPIO.input(GPIO_AC_PIN)
        return (level == GPIO.HIGH) if AC_ACTIVE_HIGH else (level == GPIO.LOW)

    def _write_status(self, ac_present: bool, soc_percent: float, voltage_v: float) -> None:
        payload = {
            "ts": time.time(),
            "ac_present": bool(ac_present),
            "soc_percent": float(round(soc_percent, 2)),
            "voltage_v": float(round(voltage_v, 3)),
        }
        tmp_path = UPS_STATUS_PATH + ".tmp"
        with open(tmp_path, "w") as f:
            json.dump(payload, f, separators=(",", ":"))
        os.replace(tmp_path, UPS_STATUS_PATH)

    def _maybe_shutdown(self, ac_present: bool, soc_percent: float) -> None:
        if self._shutdown_fired:
            return
        now = time.time()
        # Добавим проверку, что SOC не равен 0 из-за ошибки чтения
        low = (not ac_present) and (0 < soc_percent <= LOW_BATTERY_PERCENT)
        if low:
            if self._low_batt_since is None:
                self._low_batt_since = now
            held = now - self._low_batt_since
            if held >= LOW_BATT_DEBOUNCE_SEC:
                self._shutdown_fired = True
                if DRY_RUN:
                    self.log.warning(
                        "DRY_RUN: would shutdown now (SOC<=%.2f%% for %.0fs, AC=False)",
                        LOW_BATTERY_PERCENT, held
                    )
                else:
                    self.log.error(
                        "LOW BATTERY: shutting down (SOC=%.2f%%, AC=False, held %.0fs)",
                        soc_percent, held
                    )
                    try:
                        subprocess.Popen(SHUTDOWN_CMD)
                    except Exception as e:
                        self.log.exception("Failed to call shutdown: %s", e)
        else:
            self._low_batt_since = None

    def loop(self) -> None:
        try:
            while True:
                try:
                    ac = self._is_ac()
                    soc = self._read_soc()
                    volt = self._read_voltage()

                    # Пропускаем запись, если чтение было неудачным (вернулся 0)
                    if soc == 0.0 and volt == 0.0:
                        self.log.warning("Skipping update due to read failure.")
                    else:
                        if volt < 2.5 or volt > 5.5:
                            self.log.warning("Voltage out of expected range: U=%.3fV", volt)
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