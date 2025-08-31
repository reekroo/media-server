#!/usr/bin/env python3
from __future__ import annotations
from dataclasses import dataclass

DEFAULT_CACHE_TTL = 1.0

@dataclass
class BatteryConfig:
    cache_ttl: float = DEFAULT_CACHE_TTL
    render_if_missing: bool = False
    low_threshold: int = 20
    show_bolt_when_charging: bool = True
    inset: int = 2
    fg: int = 255
    bg: int = 0
