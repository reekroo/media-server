import logging
import time
import threading
from schedule import every, run_pending

from historical_data_fetcher import HistoricalDataFetcher
from outputs.json_file_output import JsonFileOutput

class DataExportScheduler:
    def __init__(self,
                 fetcher: HistoricalDataFetcher,
                 output: JsonFileOutput,
                 logger: logging.Logger,
                 output_path: str,
                 interval_minutes: int,
                 fetch_days: int):
        self._fetcher = fetcher
        self._output = output
        self._log = logger
        self._output_path = output_path
        self._interval_minutes = interval_minutes
        self._fetch_days = fetch_days
        self._stop_run_continuously = threading.Event()
        self._log.info("DataExportScheduler initialized.")

    def _job(self) -> None:
        self._log.info("Running scheduled data export job...")
        try:
            events = self._fetcher.fetch_last_n_days(self._fetch_days)
            if events:
                self._output.write(events, self._output_path)
            else:
                self._log.info("No historical events fetched, skipping file write.")
        except Exception as e:
            self._log.error(f"An error occurred in the scheduled job: {e}", exc_info=True)

    def _run_continuously(self, run_immediately: bool):
        self._log.info(f"Scheduler starting. Job will run every {self._interval_minutes} minutes.")
        
        if run_immediately:
            self._log.info("Running initial data export job immediately...")
            self._job()

        every(self._interval_minutes).minutes.do(self._job)
        while not self._stop_run_continuously.is_set():
            run_pending()
            time.sleep(1)
        self._log.info("Scheduler has been stopped.")

    def start(self, run_immediately: bool = False) -> threading.Thread:
        thread = threading.Thread(target=self._run_continuously, args=(run_immediately,), daemon=True)
        thread.start()
        self._log.info("Scheduler background thread started.")
        return thread

    def stop(self):
        self._stop_run_continuously.set()