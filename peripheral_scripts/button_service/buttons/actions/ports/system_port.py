#!/usr/bin/env python3
from __future__ import annotations

from typing import Protocol

class ISystemPower(Protocol):
    def reboot(self) -> None: ...