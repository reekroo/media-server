#!/usr/bin/env python3
from __future__ import annotations

from .base_button import BaseButton


class BarePullupButton(BaseButton):
    """
    Голая тактовая кнопка GPIO↔GND (встроенная подтяжка вверх).
    Нажатие = LOW -> active_high=False.
    """
    def __init__(self, pin: int, hold_time: float, bounce_time: float):
        super().__init__(
            pin=pin,
            hold_time=hold_time,
            bounce_time=bounce_time,
            pull_up=True,
            active_high=False,
        )
