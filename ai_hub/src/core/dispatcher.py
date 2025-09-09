from __future__ import annotations
import asyncio
import inspect
from typing import Any, Awaitable, Callable, Dict

JobFunc = Callable[..., Awaitable[Any]]

class Dispatcher:
    def __init__(self, app: Any | None = None) -> None:
        self.app = app
        self._jobs: Dict[str, JobFunc] = {}

    def set_app(self, app: Any) -> None:
        self.app = app

    def register(self, name: str, func: JobFunc) -> None:
        if not asyncio.iscoroutinefunction(func):
            raise TypeError(f"Job '{name}' must be an async function")
        self._jobs[name] = func

    async def run(self, name: str, **kwargs: Any) -> Any:
        func = self._jobs.get(name)
        if func is None:
            raise KeyError(f"Unknown job '{name}'. Registered: {', '.join(sorted(self._jobs)) or '—'}")

        sig = inspect.signature(func)
        if "app" in sig.parameters and "app" not in kwargs:
            if self.app is None:
                raise RuntimeError(f"Job '{name}' expects 'app' but dispatcher has no app set. "
                                   f"Either pass app=... or call dispatcher.set_app(app).")
            kwargs["app"] = self.app

        return await func(**kwargs)

DigestDispatcher = Dispatcher

__all__ = ["Dispatcher", "DigestDispatcher", "JobFunc"]
