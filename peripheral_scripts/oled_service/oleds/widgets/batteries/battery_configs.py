#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from dataclasses import dataclass

DEFAULT_CACHE_TTL = 1.0

@dataclass
class BatteryConfig:
    # кэш внутри виджета
    cache_ttl: float = DEFAULT_CACHE_TTL
    # если ни разу не было валидных данных — вообще не рисуем
    render_if_missing: bool = False
    # индикация «низкий уровень» (для off-AC)
    low_threshold: int = 20
    # показывать «молнию» при зарядке
    show_bolt_when_charging: bool = True
    # внутренний отступ «уровня» от рамки
    inset: int = 2
    # цвета (SSD1327: белый по чёрному)
    fg: int = 255
    bg: int = 0
    # диагностика: подпись NN% рядом с батарейкой
    debug_draw_percent: bool = False
