#!/usr/bin/env python3
from __future__ import annotations

from .base import BaseButton

class BarePullupButton(BaseButton):

    def __init__(self, pin: int, hold_time: float, bounce_time: float):
        super().__init__(
            pin=pin,
            pull_up=True,
            active_high=False,
            bounce_time=bounce_time,
            hold_time=hold_time,
        )
