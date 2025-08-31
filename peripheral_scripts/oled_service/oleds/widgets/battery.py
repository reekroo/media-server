import json, time
from typing import Optional, Tuple
from PIL import ImageDraw

try:
    from oleds.configs.configs import UPS_STATUS_PATH, UPS_STATUS_STALE_SEC
except Exception:
    UPS_STATUS_PATH = "/run/peripherals/ups/status.json"
    UPS_STATUS_STALE_SEC = 120

_CACHE: Tuple[float, Optional[dict]] = (0.0, None)
_CACHE_TTL = 1.0

def _load_status() -> Optional[dict]:
    now = time.time()
    ts, cached = _CACHE
    if now - ts < _CACHE_TTL and cached is not None:
        return cached

    st = None
    try:
        with open(UPS_STATUS_PATH, "r") as f:
            st = json.load(f)
        if abs(now - float(st.get("ts", 0))) > UPS_STATUS_STALE_SEC:
            st = None
    except Exception:
        st = None

    globals()["_CACHE"] = (now, st)
    return st

def format_battery_text() -> str:
    st = _load_status()
    if not st:
        return "— %"
    soc = int(round(float(st.get("soc_percent", 0.0))))
    ac  = bool(st.get("ac_present", False))
    return f"{'🔌' if ac else '🔋'} {soc}%"

def draw_battery(draw: ImageDraw.ImageDraw, x: int, y: int, w: int = 28, h: int = 12) -> None:
    body_w = w - 3
    draw.rectangle((x, y, x + body_w, y + h), outline=255, width=1)
    draw.rectangle((x + body_w + 1, y + h//3, x + w, y + 2*h//3), fill=255)

    st = _load_status()
    if not st:
        draw.text((x + body_w//2 - 3, y + 1), "?", fill=255)
        return

    soc = max(0.0, min(100.0, float(st.get("soc_percent", 0.0))))
    ac  = bool(st.get("ac_present", False))
    chg = bool(st.get("charging", False))

    inset = 2
    inner_w = body_w - 2*inset
    level_w = int(inner_w * soc / 100.0)

    draw.rectangle((x + inset, y + inset, x + body_w - inset, y + h - inset), fill=0)
    if level_w > 0:
        draw.rectangle((x + inset, y + inset, x + inset + level_w, y + h - inset), fill=255)

    if ac and chg:
        cx = x + body_w // 2
        cy = y + h // 2
        bolt = [(cx-3,cy-5),(cx+1,cy-5),(cx-1,cy),(cx+4,cy),(cx-2,cy+6),(cx,cy+1)]
        draw.polygon(bolt, fill=0)
        draw.line(bolt + [bolt[0]], fill=255)
    elif (not ac) and soc <= 20:
        cx = x + body_w // 2
        draw.rectangle((cx, y+2, cx+1, y+h-4), fill=0)
        draw.rectangle((cx, y+h-3, cx+1, y+h-2), fill=0)