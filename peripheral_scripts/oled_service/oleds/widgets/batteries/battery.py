#!/usr/bin/env python3
from __future__ import annotations
from PIL import ImageDraw

from .battery_widget import BatteryWidget
from .battery_configs import BatteryConfig
from .battery_status_loader import FileUPSStatusLoader, DEFAULT_UPS_STATUS_PATH, DEFAULT_UPS_STATUS_STALE_SEC

_widget = BatteryWidget(
    loader=FileUPSStatusLoader(
        path=DEFAULT_UPS_STATUS_PATH,
        stale_sec=DEFAULT_UPS_STATUS_STALE_SEC,
    ),
    config=BatteryConfig(
        render_if_missing=False,
        fg=255, bg=0,
    )
)

def format_battery_text() -> str:
    text = _widget.format_text()
    return text if text is not None else ""

def draw_battery(draw: ImageDraw.ImageDraw, x: int, y: int, w: int = 28, h: int = 12) -> None:
    try:
        drawn = _widget.draw(draw, x, y, w=w, h=h)
    except Exception:
        return