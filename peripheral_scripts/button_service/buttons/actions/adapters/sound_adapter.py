#!/usr/bin/env python3
from __future__ import annotations

from typing import Optional, Any
from ..ports.sound_port import ISound
from sounds import sound_client

class SoundClientAdapter(ISound):
    def __init__(self, logger: Optional[Any] = None):
        self.log = logger

    def play(self, name: str, *, wait: bool) -> None:
        if self.log:
            try: self.log.debug("[SoundAdapter] Play %r wait=%s", name, wait)
            except Exception: pass
        sound_client.play_sound(name, wait=wait)
