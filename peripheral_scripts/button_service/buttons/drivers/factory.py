#!/usr/bin/env python3
from __future__ import annotations

from typing import Optional

from .module_active import ModuleButton
from .bare_pullup import BarePullupButton
from .detector import probe_pin


def create_button_by_mode(mode: str, pin: int, hold: float, bounce: float, *, logger: Optional[object] = None):

    m = (mode or "").strip().lower()

    if m == "bare_pullup":
        return BarePullupButton(pin, hold, bounce)

    if m == "module_active_high":
        return ModuleButton(pin, hold, bounce, active_high=True)

    if m == "module_active_low":
        return ModuleButton(pin, hold, bounce, active_high=False)

    idle_is_high, transitions = probe_pin(pin)
    picked = "module_active_low" if idle_is_high else "module_active_high"
    if logger:
        try:
            logger.info(
                "[ButtonFactory] Auto-detect: idle_is_high=%s, transitions=%d -> %s",
                idle_is_high, transitions, picked
            )
        except Exception:
            pass

    if picked == "module_active_low":
        return ModuleButton(pin, hold, bounce, active_high=False)
    else:
        return ModuleButton(pin, hold, bounce, active_high=True)
