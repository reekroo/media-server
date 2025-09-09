from __future__ import annotations

from typing import List

class JobLauncher:
    async def run(self, job_key: str) -> List[str]:
        raise NotImplementedError

class DispatcherJobLauncher(JobLauncher):
    def __init__(self, dispatcher) -> None:
        self._dispatcher = dispatcher

    async def run(self, job_key: str) -> list[str]:
        return await self._dispatcher.run(job_key)
