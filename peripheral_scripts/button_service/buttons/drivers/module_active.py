#!/usr/bin/env python3
from __future__ import annotations

from .base import BaseButton

class ModuleButton(BaseButton):
    """
    Внешний модуль VCC/OUT/GND, уровни задаёт внешняя электроника (pull_up=None).
    active_high:
      - False -> нажатие = LOW  (типично для модулей)
      - True  -> нажатие = HIGH
    """
    def __init__(self, pin: int, hold_time: float, bounce_time: float, *, active_high: bool):
        super().__init__(
            pin=pin,
            pull_up=None,
            active_high=active_high,
            bounce_time=bounce_time,
            hold_time=hold_time,
        )
