#!/usr/bin/env python3
from __future__ import annotations

from .base_button import BaseButton


class ModuleButton(BaseButton):
    """
    Внешний модуль VCC/OUT/GND.
    pull_up=None (внешняя электроника рулит уровнем).
    active_high:
      - False -> нажатие = LOW (частый случай для таких модулей)
      - True  -> нажатие = HIGH
    """
    def __init__(self, pin: int, hold_time: float, bounce_time: float, *, active_high: bool):
        super().__init__(
            pin=pin,
            hold_time=hold_time,
            bounce_time=bounce_time,
            pull_up=None,
            active_high=active_high,
        )
