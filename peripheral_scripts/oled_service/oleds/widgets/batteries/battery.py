#!/usr/bin/env python3
from __future__ import annotations
from PIL import ImageDraw
import logging

# Мы больше не импортируем сложный виджет, так как не используем его
# from .battery_widget import BatteryWidget 
# from .battery_configs import BatteryConfig
# from .battery_status_loader import FileUPSStatusLoader, DEFAULT_UPS_STATUS_PATH, DEFAULT_UPS_STATUS_STALE_SEC

log = logging.getLogger(__name__)

def format_battery_text() -> str:
    """
    Принудительно возвращаем тестовую строку.
    """
    return "BATT TEST"

def draw_battery(draw: ImageDraw.ImageDraw, x: int, y: int, w: int = 28, h: int = 12) -> None:
    """
    Тестовая функция: полностью игнорирует логику батареи и просто
    рисует сплошной белый прямоугольник на ее месте.
    """
    try:
        # Задаем цвет напрямую (255 = белый для монохромного OLED)
        fill_color = 255
        
        # Рисуем прямоугольник, занимающий всю область виджета
        draw.rectangle(
            (x, y, x + w, y + h), 
            fill=fill_color
        )
    except Exception as e:
        # Если при отрисовке возникнет ошибка, мы увидим ее в логе
        log.error(f"[draw_battery_test] Failed to draw simple rectangle: {e}", exc_info=True)
        return