#!/usr/bin/env python3
from typing import Optional, Dict
from PIL import ImageDraw

from .battery_configs import BATTERY_WIDTH, BATTERY_HEIGHT
from .battery_status_loader import load_battery_status

_SOC_KEY = "soc_display_percent"

def format_battery_text() -> str:
    status = load_battery_status()        
    if not status or _SOC_KEY not in status:
        return "BATT: N/A"
    
    soc = int(round(status[_SOC_KEY]))
    ac  = bool(status.get("ac_present", False))
    
    icon = "🔌" if ac else "🔋"
    return f"{icon} {soc}%"

def draw_battery(draw: ImageDraw.ImageDraw, x: int, y: int, w: int = BATTERY_WIDTH, h: int = BATTERY_HEIGHT) -> None:
    fg_color = 255
    bg_color = 0
    body_w = w - 3
    
    draw.rectangle((x, y, x + body_w, y + h), outline=fg_color, width=1)
    draw.rectangle((x + body_w + 1, y + h // 3, x + w, y + 2 * h // 3), fill=fg_color)
    
    status = load_battery_status()
    if not status or _SOC_KEY not in status:
        return

    soc = max(0.0, min(100.0, status[_SOC_KEY]))
    inset = 2
    inner_w = body_w - (2 * inset)
    if inner_w < 1: 
        return

    level_w = int(inner_w * soc / 100.0)
    
    draw.rectangle((x + inset, y + inset, x + body_w - inset, y + h - inset), fill=bg_color)
    
    if level_w > 0:
        x0 = x + inset
        y0 = y + inset
        x1 = x + inset + level_w
        y1 = y + h - inset
        
        for line_y in range(y0, y1):
            draw.line((x0, line_y, x1, line_y), fill=fg_color)