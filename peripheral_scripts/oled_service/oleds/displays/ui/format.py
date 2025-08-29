# oleds/displays/ui/format.py
from __future__ import annotations
import re

def fmt_bytes(b) -> str:
    try:
        b = float(b)
    except Exception:
        return "0"
    
    if b <= 0: return "0"
    
    KB, MB, GB, TB = 1024, 1024**2, 1024**3, 1024**4
    
    if b >= TB: return f"{b/TB:.1f}T"
    if b >= GB: return f"{b/GB:.1f}G"
    if b >= MB: return f"{b/MB:.0f}M"
    return f"{b/KB:.0f}K"

def parse_rate_bps(s) -> float:
    if s is None: return 0.0
    if isinstance(s, (int, float)):
        return max(0.0, float(s))
    
    s = str(s).strip().lower().replace("/s", "")
    m = re.match(r"^([0-9]+(?:\.[0-9]+)?)([km]?)$", s)
    
    if m:
        val = float(m.group(1)); unit = m.group(2)
        if unit == "m": val *= 1024*1024
        elif unit == "k": val *= 1024
        return max(0.0, val)
    try:
        return max(0.0, float(re.sub(r"[^0-9.]", "", s) or 0.0))
    except Exception:
        return 0.0

def fmt_bps(x: float) -> str:
    try:
        x = float(x)
    except Exception:
        return "0K/s"
    if x >= 1024*1024: return f"{x/(1024*1024):.1f}M/s"
    return f"{x/1024:.0f}K/s"

def short_ip(ip: str) -> str:
    try:
        parts = str(ip).split(".")
        if len(parts) == 4:
            return f"IP …{parts[-2]}.{parts[-1]}"
    except Exception:
        pass
    return "IP N/A"
