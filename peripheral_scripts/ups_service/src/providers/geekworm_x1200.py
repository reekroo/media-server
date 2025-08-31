#!/usr/bin/env python3
import smbus2
import RPi.GPIO as GPIO

from .base import UpsProvider, UpsReading
from ..configs import SETTINGS

class GeekwormX1200(UpsProvider):

    def __init__(self):
        self._bus = smbus2.SMBus(SETTINGS.i2c_bus)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(
            SETTINGS.gpio_ac_pin,
            GPIO.IN,
            pull_up_down=GPIO.PUD_DOWN if SETTINGS.ac_active_high else GPIO.PUD_UP,
        )

    def read(self) -> UpsReading:
        soc_data = self._bus.read_i2c_block_data(SETTINGS.i2c_addr, 0x04, 2)
        soc_raw = (soc_data[0] << 8) | soc_data[1]
        soc = max(0.0, min(100.0, soc_raw / 256.0))

        volt_data = self._bus.read_i2c_block_data(SETTINGS.i2c_addr, 0x02, 2)
        volt_raw = (volt_data[0] << 8) | volt_data[1]
        voltage = (volt_raw * 78.125) / 1_000_000.0

        level = GPIO.input(SETTINGS.gpio_ac_pin)
        ac_present = (level == GPIO.HIGH) if SETTINGS.ac_active_high else (level == GPIO.LOW)

        return UpsReading(soc_percent=soc, voltage_v=voltage, ac_present=ac_present)

    def cleanup(self) -> None:
        try:
            self._bus.close()
        finally:
            GPIO.cleanup()