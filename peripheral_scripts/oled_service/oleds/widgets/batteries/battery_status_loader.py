#!/usr/bin/env python3
import json
import time
from typing import Optional, Dict

from .battery_configs import UPS_STATUS_PATH, CACHE_TTL_SEC

_CACHE = {"ts": 0.0, "data": None}

def load_battery_status() -> Optional[Dict]:
    now = time.time()
    if now - _CACHE["ts"] < CACHE_TTL_SEC and _CACHE["data"] is not None:
        return _CACHE["data"]

    status_data = None
    try:
        with open(UPS_STATUS_PATH, "r") as f:
            status_data = json.load(f)
    except Exception:
        pass

    _CACHE["ts"] = now
    _CACHE["data"] = status_data
    return status_data