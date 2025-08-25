#!/usr/bin/env python3
from __future__ import annotations

from typing import Protocol

class ISound(Protocol):
    def play(self, name: str, *, wait: bool) -> None: ...