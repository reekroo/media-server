import smbus2
import RPi.GPIO as GPIO
import time
from .ups_reading_interface import UpsProvider, UpsReading

class GeekwormX1200(UpsProvider):
    def __init__(self, i2c_bus: int, i2c_addr: int, gpio_ac_pin: int, ac_active_high: bool):
        self._i2c_addr = i2c_addr
        self._gpio_ac_pin = gpio_ac_pin
        self._ac_active_high = ac_active_high
        
        self._bus = smbus2.SMBus(i2c_bus)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(
            self._gpio_ac_pin,
            GPIO.IN,
            pull_up_down=GPIO.PUD_DOWN if self._ac_active_high else GPIO.PUD_UP,
        )

    def _read_word_robustly(self, reg: int) -> int:
        for _ in range(3):
            try:
                data = self._bus.read_i2c_block_data(self._i2c_addr, reg, 2)
                return (data[0] << 8) | data[1]
            except IOError:
                time.sleep(0.1)
        return 0 

    def read(self) -> UpsReading:
        soc_raw = self._read_word_robustly(0x04)
        soc = max(0.0, min(100.0, soc_raw / 256.0))

        volt_raw = self._read_word_robustly(0x02)
        voltage = (volt_raw * 78.125) / 1_000_000.0

        level = GPIO.input(self._gpio_ac_pin)
        ac_present = (level == GPIO.HIGH) if self._ac_active_high else (level == GPIO.LOW)

        return UpsReading(soc_percent=soc, voltage_v=voltage, ac_present=ac_present)

    def cleanup(self) -> None:
        try:
            self._bus.close()
        finally:
            GPIO.cleanup()