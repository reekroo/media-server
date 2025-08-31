#!/usr/bin/env python3
from __future__ import annotations
import time
from typing import Optional, Tuple, Dict, Any
from PIL import ImageDraw 
# --- УБРАЛИ ИМПОРТ IMAGEFONT ---

from .battery_configs import BatteryConfig
from .battery_status_loader import StatusLoader

def is_status_plausible(new_st: Dict[str, Any], old_st: Optional[Dict[str, Any]]) -> bool:
    if not old_st: return True
    old_soc = old_st.get("soc_percent", 0.0)
    new_soc = new_st.get("soc_percent", 0.0)
    ac_present = new_st.get("ac_present", False)
    if old_soc < 1.0 and new_soc > 1.0: return True
    if not ac_present and new_soc > old_soc + 2.0: return False
    if abs(new_soc - old_soc) > 40.0: return False
    return True

class BatteryWidget:
    def __init__(self, loader: StatusLoader, config: BatteryConfig | None = None):
        self.loader = loader
        self.cfg = config or BatteryConfig()
        self._cache: Tuple[float, Optional[dict]] = (0.0, None)
        self._last_good: Optional[dict] = None
        # --- УБРАЛИ ЗАГРУЗКУ ШРИФТА ---

    def _get_status_cached(self) -> Optional[dict]:
        now = time.time()
        ts, cached = self._cache
        if cached is not None and (now - ts) < self.cfg.cache_ttl:
            return cached
        st = self.loader.load()
        if st:
            if is_status_plausible(st, self._last_good):
                self._last_good = st
            else:
                st = self._last_good
        else:
            st = self._last_good
        self._cache = (now, st)
        return st

    def format_text(self) -> str:
        st = self._get_status_cached()
        if not st: return "Нет данных"
        soc = int(round(float(st.get("soc_percent", 0.0))))
        ac  = bool(st.get("ac_present", False))
        if ac: return f"🔌 {soc}%"
        return f"🔋 {soc}%"

    def draw(self, draw: ImageDraw.ImageDraw, x: int, y: int, w: int = 28, h: int = 12,
             fg: Optional[int] = None, bg: Optional[int] = None) -> int:
        
        fg = self.cfg.fg if fg is None else fg
        bg = self.cfg.bg if bg is None else bg
        
        st = self._get_status_cached()
        if not st and not self.cfg.render_if_missing: return 0

        # --- ИСПОЛЬЗУЕМ СТАРУЮ, НАДЕЖНУЮ ЛОГИКУ ОТРИСОВКИ ---
        body_w = w - 3
        draw.rectangle((x, y, x + body_w, y + h), outline=fg, width=1)
        draw.rectangle((x + body_w + 1, y + h//3, x + w, y + 2*h//3), fill=fg)

        if not st:
            # Рисуем знак вопроса, если данных нет, как в старой версии
            draw.text((x + body_w//2 - 3, y + 1), "?", fill=fg)
            return w
        
        soc = max(0.0, min(100.0, float(st.get("soc_percent", 0.0))))
        ac  = bool(st.get("ac_present", False))
        chg = bool(st.get("charging", False))

        inset = self.cfg.inset
        inner_w = body_w - 2*inset
        level_w = int(inner_w * soc / 100.0)

        # Сначала рисуем черный фон внутри
        draw.rectangle((x + inset, y + inset, x + body_w - inset, y + h - inset), fill=bg)
        # Затем рисуем белый уровень заряда
        if level_w > 0:
            draw.rectangle((x + inset, y + inset, x + inset + level_w, y + h - inset), fill=fg)
        
        # Индикаторы (молния, и т.д.)
        if ac and chg:
            cx = x + body_w // 2; cy = y + h // 2
            bolt = [(cx-3,cy-5),(cx+1,cy-5),(cx-1,cy),(cx+4,cy),(cx-2,cy+6),(cx,cy+1)]
            draw.polygon(bolt, fill=bg); draw.line(bolt + [bolt[0]], fill=fg)
        elif (not ac) and soc <= self.cfg.low_threshold:
            cx = x + body_w // 2
            draw.rectangle((cx, y+2, cx+1, y+h-4), fill=bg)
            draw.rectangle((cx, y+h-3, cx+1, y+h-2), fill=bg)
        
        # Рисуем текст с процентами, если включено, но БЕЗ объекта font
        if self.cfg.debug_draw_percent:
            try:
                txt = f"{int(round(soc))}%"
                draw.text((x + w + 2, y), txt, fill=fg)
            except Exception:
                pass
        
        return w