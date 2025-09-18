import threading
import logging
from typing import Callable

class PeriodicTaskRunner:
    def __init__(self, task_callable: Callable, interval: int, logger: logging.Logger, name: str = "TaskRunner"):
        self._task_callable = task_callable
        self._interval = interval
        self._logger = logger
        self._name = name
        self._stop_event = threading.Event()
        self._thread = None

    def start(self, run_immediately: bool = False):
        self._logger.info(f"Starting {self._name} with interval {self._interval}s...")
        self._thread = threading.Thread(target=self._run_loop, args=(run_immediately,), name=self._name, daemon=True)
        self._thread.start()

    def _run_loop(self, run_immediately: bool):
        if run_immediately:
            self._execute_task()
        
        while not self._stop_event.is_set():
            self._stop_event.wait(timeout=self._interval)
            if not self._stop_event.is_set():
                self._execute_task()
        
        self._logger.info(f"{self._name} has stopped.")
        
    def _execute_task(self):
        try:
            self._logger.info(f"{self._name}: Executing task...")
            self._task_callable()
            self._logger.info(f"{self._name}: Task finished.")
        except Exception as e:
            self._logger.error(f"{self._name}: An error occurred during task execution: {e}", exc_info=True)

    def stop(self):
        self._logger.info(f"Stopping {self._name}...")
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)