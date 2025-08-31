#!/usr/bin/env python3
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple

@dataclass(frozen=True)
class BarConfig:
    pad_top: int = 2
    pad_bot: int = 2
    elem_h: int = 16
    gap: int = 2
    right_gap_between: int = 2
    clock_fmt: str = "%H:%M"
    battery_width: int = 20
    left_icons: Tuple[str, ...] = ("storage", "nvme", "bluetooth", "wifi", "docker")