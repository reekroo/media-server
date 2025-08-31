#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Финальная версия. Использует отрисовку линиями вместо заливки.
import json
import time
from typing import Optional, Dict
from PIL import ImageDraw

# --- Конфигурация ---
UPS_STATUS_PATH = "/run/peripherals/ups/status.json"
UPS_STATUS_STALE_SEC = 120
CACHE_TTL_SEC = 1.0

# --- Глобальный кеш ---
_CACHE = {"ts": 0.0, "data": None}

def _load_status() -> Optional[Dict]:
    now = time.time()
    if now - _CACHE["ts"] < CACHE_TTL_SEC and _CACHE["data"] is not None:
        return _CACHE["data"]
    status_data = None
    try:
        with open(UPS_STATUS_PATH, "r") as f: data = json.load(f)
        if abs(now - float(data.get("ts", 0))) <= UPS_STATUS_STALE_SEC: status_data = data
    except Exception: pass
    _CACHE["ts"] = now
    _CACHE["data"] = status_data
    return status_data

def format_battery_text() -> str:
    st = _load_status()
    if not st: return "BATT: N/A"
    soc = int(round(float(st.get("soc_percent", 0.0))))
    ac  = bool(st.get("ac_present", False))
    icon = "🔌" if ac else "🔋"
    return f"{icon} {soc}%"

def draw_battery(draw: ImageDraw.ImageDraw, x: int, y: int, w: int = 28, h: int = 12) -> None:
    fg_color = 255; bg_color = 0
    body_w = w - 3
    
    # Рисуем контур и "носик"
    draw.rectangle((x, y, x + body_w, y + h), outline=fg_color, width=1)
    draw.rectangle((x + body_w + 1, y + h // 3, x + w, y + 2 * h // 3), fill=fg_color)
    
    st = _load_status()
    if not st: return

    soc = max(0.0, min(100.0, float(st.get("soc_percent", 0.0))))
    inset = 2
    inner_w = body_w - (2 * inset)
    if inner_w < 1: return

    level_w = int(inner_w * soc / 100.0)
    
    # Рисуем черный фон (это должно работать, т.к. outline работает)
    draw.rectangle((x + inset, y + inset, x + body_w - inset, y + h - inset), fill=bg_color)
    
    if level_w > 0:
        # --- ОБХОДНОЙ ПУТЬ: РИСУЕМ ЗАЛИВКУ ЛИНИЯМИ ---
        # Координаты области для заливки
        x0 = x + inset
        y0 = y + inset
        x1 = x + inset + level_w
        y1 = y + h - inset
        
        # Рисуем множество горизонтальных линий от верха до низа
        for line_y in range(y0, y1):
            draw.line((x0, line_y, x1, line_y), fill=fg_color)