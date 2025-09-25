import logging
import json
import os
from pathlib import Path

from .base import IOutputStrategy
from models.weather_data import WeatherData

class FileOutput(IOutputStrategy):
    def __init__(self, file_path: str, logger: logging.Logger):
        self._file_path = Path(file_path)
        self._log = logger
        self._ensure_dir_exists()

    def _ensure_dir_exists(self):
        try:
            self._file_path.parent.mkdir(parents=True, exist_ok=True)
            self._log.info(f"Directory {self._file_path.parent} is ready for file output.")
        except Exception as e:
            self._log.error(f"Could not create directory {self._file_path.parent}: {e}")

    def output(self, data: WeatherData):
        if data is None:
            self._log.warning("No data to output to file.")
            return

        self._log.info(f"Writing latest weather data to {self._file_path}...")
        try:
            temp_path = self._file_path.with_suffix('.tmp')
            
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data._asdict(), f, ensure_ascii=False, indent=4)
            
            os.rename(temp_path, self._file_path)
            self._log.info(f"Successfully wrote weather data to {self._file_path}")

        except (IOError, OSError) as e:
            self._log.error(f"Failed to write weather data to {self._file_path}: {e}")
        except Exception as e:
            self._log.error(f"An unexpected error occurred during file output: {e}")

    def close(self):
        self._log.info("File output handler does not require closing.")
        pass