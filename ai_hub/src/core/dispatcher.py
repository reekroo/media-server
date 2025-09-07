import logging
from typing import Dict, Callable, Awaitable

logger = logging.getLogger(__name__)

class DigestDispatcher:
    def __init__(self):
        self._jobs: Dict[str, Callable[..., Awaitable]] = {}

    def register(self, name: str, job_func: Callable[..., Awaitable]):
        logger.info(f"Registering job '{name}' in dispatcher.")
        self._jobs[name] = job_func

    async def run(self, name: str, **kwargs) -> list[str]:
        if name not in self._jobs:
            logger.error(f"Attempted to run unregistered job: {name}")
            return [f"Error: Job '{name}' is not registered."]
        
        job_func = self._jobs[name]
        result = await job_func(**kwargs)

        if isinstance(result, str): return [result]
        if isinstance(result, list): return result
        return []