#!/usr/bin/env python3
from __future__ import annotations
import json, time, re, os, logging
from dataclasses import dataclass
from typing import Optional, Protocol, Dict, Any

log = logging.getLogger(__name__) # <--- Получаем экземпляр настроенного логгера

def _detect_status_path() -> str:
    # 1) из твоего configs.py, если он есть в PYTHONPATH
    try:
        from oleds.configs import UPS_STATUS_PATH as CFG_PATH  # type: ignore
        if isinstance(CFG_PATH, str) and CFG_PATH:
            return CFG_PATH
    except Exception:
        pass
    # 2) из переменной окружения
    env = os.environ.get("UPS_STATUS_PATH")
    if env:
        return env
    # 3) дефолт
    return "/run/peripherals/ups/status.json"

DEFAULT_UPS_STATUS_PATH = _detect_status_path()
DEFAULT_UPS_STATUS_STALE_SEC = 120

class StatusLoader(Protocol):
    def load(self) -> Optional[dict]:
        ...

_NUM = re.compile(r"-?\d+(?:\.\d+)?")

def _to_float(x: Any, default: float = 0.0) -> float:
    if x is None:
        return default
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x)
    m = _NUM.search(s)
    if not m:
        return default
    try:
        return float(m.group(0))
    except Exception:
        return default

def _to_bool(x: Any) -> bool:
    if isinstance(x, bool):
        return x
    if x is None:
        return False
    return str(x).strip().lower() in {"1", "true", "yes", "y", "on"}

def _pick(d: Dict[str, Any], *names: str) -> Any:
    for n in names:
        if n in d:
            return d[n]
    lower = {k.lower(): k for k in d.keys()}
    for n in names:
        k = lower.get(n.lower())
        if k:
            return d[k]
    return None

def _normalize_status(raw: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not isinstance(raw, dict):
        return None

    ts = _to_float(_pick(raw, "ts", "timestamp", "time", "t"), 0.0)

    soc_val = _pick(raw, "soc_percent", "soc", "SOC", "battery_percent", "percent")
    soc = _to_float(soc_val, 0.0)
    if 0.0 <= soc <= 1.0 and isinstance(soc_val, (int, float)):
        soc *= 100.0
    soc = max(0.0, min(100.0, soc))

    ac_present = _to_bool(_pick(raw, "ac_present", "ac", "on_ac", "mains", "grid", "power_ac"))
    
    charging_val = _pick(raw, "charging", "is_charging", "charge", "charging_state")
    if charging_val is None:
        charging = ac_present
    else:
        charging = _to_bool(charging_val)

    result = {
        "ts": float(ts),
        "soc_percent": float(soc),
        "ac_present": bool(ac_present),
        "charging": bool(charging),
    }

    if "voltage_v" in raw:
        result["voltage_v"] = _to_float(raw["voltage_v"], 0.0)
    elif "U" in raw or "voltage" in raw:
        result["voltage_v"] = _to_float(_pick(raw, "U", "voltage"), 0.0)
    return result

@dataclass
class FileUPSStatusLoader:
    path: str = DEFAULT_UPS_STATUS_PATH
    stale_sec: int = DEFAULT_UPS_STATUS_STALE_SEC

    def load(self) -> Optional[dict]:
        now = time.time()
        try:
            with open(self.path, "r") as f:
                raw = json.load(f)
        except Exception as e:
            # <--- ЗАПИСЫВАЕМ В ЛОГ ТОЧНУЮ ОШИБКУ
            log.error(f"Failed to load/parse UPS status file {self.path}: {e}")
            return None
        
        st = _normalize_status(raw)
        if not st:
            log.warning(f"Failed to normalize data from {self.path}")
            return None
            
        ts = _to_float(st.get("ts"), 0.0)
        if abs(now - ts) > self.stale_sec:
            log.warning(f"UPS status file {self.path} is stale (ts: {ts})")
            return None
            
        return st