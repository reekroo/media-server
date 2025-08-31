#!/usr/bin/env python3
from __future__ import annotations
import time
from typing import Optional, Tuple
from PIL import ImageDraw

from .battery_configs import BatteryConfig
from .battery_status_loader import StatusLoader

class BatteryWidget:
    def __init__(self, loader: StatusLoader, config: BatteryConfig | None = None):
        self.loader = loader
        self.cfg = config or BatteryConfig()
        self._cache: Tuple[float, Optional[dict]] = (0.0, None)

    def _get_status_cached(self) -> Optional[dict]:
        now = time.time()
        ts, cached = self._cache
        if cached is not None and (now - ts) < self.cfg.cache_ttl:
            return cached
        st = self.loader.load()
        self._cache = (now, st)
        return st

    def format_text(self) -> Optional[str]:
        st = self._get_status_cached()
        if not st:
            return None
        
        soc = int(round(float(st.get("soc_percent", 0.0))))
        ac  = bool(st.get("ac_present", False))
        return f"{'🔌' if ac else '🔋'} {soc}%"

    def draw(self, draw: ImageDraw.ImageDraw, x: int, y: int, w: int = 28, h: int = 12, fg: Optional[int] = None, bg: Optional[int] = None) -> int:
        
        fg = self.cfg.fg if fg is None else fg
        bg = self.cfg.bg if bg is None else bg

        st = None
        try:
            st = self._get_status_cached()
        except Exception:
            st = None

        if not st and not self.cfg.render_if_missing:
            return 0

        body_w = max(6, w - 3)

        try:
            draw.rectangle((x, y, x + body_w, y + h), outline=fg, width=1)
            draw.rectangle((x + body_w + 1, y + h//3, x + w, y + 2*h//3), fill=fg)
        except Exception:
            return 0

        if not st:
            if self.cfg.render_if_missing:
                draw.text((x + body_w//2 - 3, y + 1), "?", fill=fg)
                return w
            return 0

        soc = max(0.0, min(100.0, float(st.get("soc_percent", 0.0))))
        ac  = bool(st.get("ac_present", False))
        chg = bool(st.get("charging", False))

        inset = max(1, min(self.cfg.inset, min(body_w//3, h//3)))
        inner_w = max(0, body_w - 2*inset)
        level_w = int(round(inner_w * soc / 100.0))

        draw.rectangle((x + inset, y + inset, x + body_w - inset, y + h - inset), fill=bg)
        if level_w > 0:
            draw.rectangle((x + inset, y + inset, x + inset + level_w, y + h - inset), fill=fg)

        if self.cfg.show_bolt_when_charging and ac and chg:
            cx = x + body_w // 2
            cy = y + h // 2
            bolt = [(cx-3,cy-5),(cx+1,cy-5),(cx-1,cy),(cx+4,cy),(cx-2,cy+6),(cx,cy+1)]
            draw.polygon(bolt, fill=bg)
            draw.line(bolt + [bolt[0]], fill=fg)
        elif (not ac) and soc <= self.cfg.low_threshold:
            cx = x + body_w // 2
            draw.rectangle((cx, y+2, cx+1, y+h-4), fill=bg)
            draw.rectangle((cx, y+h-3, cx+1, y+h-2), fill=bg)

        return w