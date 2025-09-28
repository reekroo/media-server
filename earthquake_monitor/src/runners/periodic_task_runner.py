import asyncio
import logging
from typing import Callable, Awaitable

class PeriodicTaskRunner:
    def __init__(self, task_callable: Callable[[], Awaitable[None]], interval: int, logger: logging.Logger, name: str):
        self._task_callable = task_callable
        self._interval = interval
        self._logger = logger
        self._name = name
        self._task: asyncio.Task | None = None

    def start(self, run_immediately: bool = False):
        self._logger.info(f"Scheduling '{self._name}' with interval {self._interval}s...")
        self._task = asyncio.create_task(self._run_loop(run_immediately))

    async def stop(self):
        if self._task and not self._task.done():
            self._logger.info(f"Stopping '{self._name}'...")
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                self._logger.info(f"'{self._name}' was successfully stopped.")

    async def _run_loop(self, run_immediately: bool):
        if run_immediately:
            await self._execute_task()
        
        while True:
            try:
                await asyncio.sleep(self._interval)
                await self._execute_task()
            except asyncio.CancelledError:
                break
        
    async def _execute_task(self):
        try:
            self._logger.info(f"'{self._name}': Executing task...")
            await self._task_callable()
            self._logger.info(f"'{self._name}': Task finished.")
        except Exception as e:
            self._logger.error(f"'{self._name}': An error occurred during task execution: {e}", exc_info=True)