import os
import json
import time

from .providers.ups_reading_interface import UpsReading

class StatusWriter:
    def __init__(self, path: str):
        self._path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
    def write(self, reading: UpsReading, display_soc: float):
        payload = {
            "ts": time.time(),
            "ac_present": reading.ac_present,
            "voltage_v": float(round(reading.voltage_v, 3)),
            "soc_chip_percent": float(round(reading.soc_percent, 2)),
            "soc_display_percent": float(round(display_soc, 2)),
        }
        tmp_path = self._path + ".tmp"
        with open(tmp_path, "w") as f:
            json.dump(payload, f, separators=(",", ":"))
        os.replace(tmp_path, self._path)