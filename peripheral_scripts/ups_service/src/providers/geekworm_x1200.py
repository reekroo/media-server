import smbus2
import RPi.GPIO as GPIO

from .base import UpsProvider, UpsReading
from ..configs import SETTINGS

def _read_word_swapped(bus: smbus2.SMBus, addr: int, reg: int) -> int:
    val = bus.read_word_data(addr, reg)
    lo = val & 0xFF
    hi = (val >> 8) & 0xFF
    return (hi << 8) | lo

class GeekwormX1200(UpsProvider):
    def __init__(self):
        self._bus = smbus2.SMBus(SETTINGS.i2c_bus)
        GPIO.setmode(GPIO.BCM)

        GPIO.setup(
            SETTINGS.gpio_ac_pin,
            GPIO.IN,
            pull_up_down=GPIO.PUD_DOWN if SETTINGS.ac_active_high else GPIO.PUD_UP
        )

    def read(self) -> UpsReading:
        soc_raw = _read_word_swapped(self._bus, SETTINGS.i2c_addr, 0x04)
        volt_raw = _read_word_swapped(self._bus, SETTINGS.i2c_addr, 0x02)

        soc = max(0.0, min(100.0, soc_raw / 256.0))
        voltage = (volt_raw * 78.125) / 1_000_000.0

        level = GPIO.input(SETTINGS.gpio_ac_pin)
        ac_present = (level == GPIO.HIGH) if SETTINGS.ac_active_high else (level == GPIO.LOW)

        return UpsReading(soc_percent=soc, voltage_v=voltage, ac_present=ac_present)

    def cleanup(self) -> None:
        try:
            self._bus.close()
        finally:
            GPIO.cleanup()
