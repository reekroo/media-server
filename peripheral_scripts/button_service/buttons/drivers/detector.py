#!/usr/bin/env python3
from __future__ import annotations

import time
from typing import Tuple

from gpiozero import DigitalInputDevice


def probe_pin(pin: int, sample_time: float = 0.3, interval: float = 0.005) -> Tuple[bool, int]:
    """
    Пробуем понять "уровень покоя" и количество переходов.
    pull_up=None, active_state=True: is_active == HIGH.
    Возвращает: (idle_is_high, transitions)
    """
    dev = DigitalInputDevice(pin=pin, pull_up=None, active_state=True, bounce_time=None)
    try:
        ones = 0
        total = 0
        transitions = 0
        prev = bool(dev.is_active)
        start = time.monotonic()
        while time.monotonic() - start < sample_time:
            cur = bool(dev.is_active)
            ones += 1 if cur else 0
            total += 1
            if cur != prev:
                transitions += 1
                prev = cur
            time.sleep(interval)

        idle_is_high = (ones / max(1, total)) >= 0.5
        return idle_is_high, transitions
    finally:
        try:
            dev.close()
        except Exception:
            pass
