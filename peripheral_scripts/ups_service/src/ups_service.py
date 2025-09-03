import time
import logging

from .providers.ups_reading_interface import UpsProvider
from .shutdown_policy import ShutdownPolicy
from .status_writer import StatusWriter
from .display_soc_calculator import DisplaySoCCalculator

class UpsService:
    def __init__(self, provider: UpsProvider, policy: ShutdownPolicy, writer: StatusWriter, soc_calc: DisplaySoCCalculator, logger: logging.Logger, poll_interval: float):
        self._provider = provider
        self._policy = policy
        self._writer = writer
        self._soc_calc = soc_calc
        self._log = logger
        self._poll_interval = poll_interval
        
        self._log.info("UPS Service started.")

    def loop(self):
        try:
            while True:
                try:
                    reading = self._provider.read()
                    
                    if reading.voltage_v > 0.1:
                        display_soc = self._soc_calc.calculate(reading.voltage_v, reading.ac_present)
                        self._writer.write(reading, display_soc)
                        self._policy.check(reading)
                        
                        self._log.info(f"AC={reading.ac_present} SOC_chip={reading.soc_percent:.1f}% "
                                     f"SOC_display={display_soc:.1f}% U={reading.voltage_v:.3f}V")

                except Exception as e:
                    self._log.exception(f"Error in main loop: {e}")
                
                time.sleep(self._poll_interval)
        finally:
            self._provider.cleanup()