#!/usr/bin/env python3
from __future__ import annotations
import json, time
from dataclasses import dataclass
from typing import Optional, Protocol

DEFAULT_UPS_STATUS_PATH = "/run/peripherals/ups/status.json"
DEFAULT_UPS_STATUS_STALE_SEC = 120

class StatusLoader(Protocol):
    def load(self) -> Optional[dict]:
        ...

@dataclass
class FileUPSStatusLoader:
    path: str = DEFAULT_UPS_STATUS_PATH
    stale_sec: int = DEFAULT_UPS_STATUS_STALE_SEC

    def load(self) -> Optional[dict]:
        now = time.time()
        try:
            with open(self.path, "r") as f:
                st = json.load(f)
        except Exception:
            return None
        try:
            ts = float(st.get("ts", 0))
        except Exception:
            return None
        if abs(now - ts) > self.stale_sec:
            return None
        return st
