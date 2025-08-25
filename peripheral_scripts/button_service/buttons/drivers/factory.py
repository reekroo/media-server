#!/usr/bin/env python3
from __future__ import annotations

import time
from typing import Tuple

from gpiozero import DigitalInputDevice

from .bare_pullup import BarePullupButton
from .module_active import ModuleButton


def _probe_pin(pin: int, sample_s: float = 0.8) -> Tuple[bool, int, int]:
    """
    Читает пин ~0.8s (без внутренней подтяжки).
    Возвращает (idle_is_high, ones, transitions).

    ВАЖНО: при pull_up=None у gpiozero нужен active_state, иначе PinInvalidState.
    Для «сырых» чтений выставляем active_state=True (без инверсий).
    """
    dev = DigitalInputDevice(pin, pull_up=None, active_state=True, bounce_time=0.05)
    try:
        t0 = time.monotonic()
        last = dev.value
        transitions = 0
        samples = 1
        ones = 1 if last else 0

        while time.monotonic() - t0 < sample_s:
            v = dev.value
            if v != last:
                transitions += 1
                last = v
            samples += 1
            ones += 1 if v else 0
            time.sleep(0.01)

        idle_is_high = (ones / samples) >= 0.5
        return idle_is_high, ones, transitions
    finally:
        try:
            dev.close()
        except Exception:
            pass


def create_button_auto(pin: int, hold: float, bounce: float):
    """
    AUTO:
      - если сильно «плавает» -> BarePullupButton (вкл. внутренний pull-up)
      - если стабильно HIGH   -> модуль active-low  (нажатие = LOW)
      - если стабильно LOW    -> модуль active-high (нажатие = HIGH)
    """
    idle_is_high, _ones, transitions = _probe_pin(pin)
    if transitions > 20:
        return BarePullupButton(pin, hold, bounce)
    if idle_is_high:
        return ModuleButton(pin, hold, bounce, active_high=False)  # active-low
    else:
        return ModuleButton(pin, hold, bounce, active_high=True)   # active-high


def create_button_by_mode(mode: str, pin: int, hold: float, bounce: float):
    """
    Явные режимы: "bare_pullup" | "module_active_low" | "module_active_high" | "auto"
    """
    m = (mode or "").strip().lower()
    if m == "bare_pullup":
        return BarePullupButton(pin, hold, bounce)
    if m == "module_active_low":
        return ModuleButton(pin, hold, bounce, active_high=False)
    if m == "module_active_high":
        return ModuleButton(pin, hold, bounce, active_high=True)
    return create_button_auto(pin, hold, bounce)
