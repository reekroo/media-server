#!/usr/bin/env python3
from __future__ import annotations

import os
from dataclasses import dataclass

DEFAULT_PIN = 5               # BCM5 (29 pin)
DEFAULT_BOUNCE = 0.6
DEFAULT_HOLD = 3.5
DEFAULT_BUTTON_COOLDOWN = 0.8
DEFAULT_STARTUP_GRACE = 1.0
DEFAULT_MODE = "auto"         # "auto" | "bare_pullup" | "module_active_low" | "module_active_high"

DEFAULT_SOUND_SHORT = "WIFI_TOGGLE"
DEFAULT_SOUND_LONG  = "REBOOT_SYSTEM"

@dataclass
class Settings:
    pin: int = DEFAULT_PIN
    bounce: float = DEFAULT_BOUNCE
    hold: float = DEFAULT_HOLD
    cooldown: float = DEFAULT_BUTTON_COOLDOWN
    startup_grace: float = DEFAULT_STARTUP_GRACE
    mode: str = DEFAULT_MODE
    sound_short: str = DEFAULT_SOUND_SHORT
    sound_long: str = DEFAULT_SOUND_LONG


def load_settings() -> Settings:
    s = Settings()

    try:
        from . import hardware_pins as hp
        s.pin          = int(getattr(hp, "BUTTON_PIN", s.pin))
        s.bounce       = float(getattr(hp, "BUTTON_BOUNCE_TIME", s.bounce))
        s.hold         = float(getattr(hp, "BUTTON_HOLD_TIME", s.hold))
        s.cooldown     = float(getattr(hp, "BUTTON_COOLDOWN", s.cooldown))

        if hasattr(hp, "BUTTON_ACTIVE_HIGH"):
            ah         = bool(getattr(hp, "BUTTON_ACTIVE_HIGH"))
            s.mode     = "module_active_high" if ah else "module_active_low"
        s.mode         = str(getattr(hp, "BUTTON_MODE", s.mode))

        s.sound_short  = str(getattr(hp, "BUTTON_SOUND_SHORT", s.sound_short))
        s.sound_long   = str(getattr(hp, "BUTTON_SOUND_LONG", s.sound_long))
    except Exception:
        pass

    s.pin           = int(os.getenv("BUTTON_PIN", s.pin))
    s.bounce        = float(os.getenv("BUTTON_BOUNCE_TIME", s.bounce))
    s.hold          = float(os.getenv("BUTTON_HOLD_TIME", s.hold))
    s.cooldown      = float(os.getenv("BUTTON_COOLDOWN", s.cooldown))
    s.startup_grace = float(os.getenv("BUTTON_STARTUP_GRACE_S", s.startup_grace))
    s.mode          = os.getenv("BUTTON_MODE", s.mode)
    s.sound_short   = os.getenv("BUTTON_SOUND_SHORT", s.sound_short)
    s.sound_long    = os.getenv("BUTTON_SOUND_LONG",  s.sound_long)

    return s
