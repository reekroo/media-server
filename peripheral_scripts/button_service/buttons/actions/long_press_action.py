#!/usr/bin/env python3
from __future__ import annotations

import time
from typing import Optional, Any
from .ports.sound_port import ISound
from .ports.system_port import ISystemPower

class LongPressAction:

    def __init__(
        self,
        sound: ISound,
        power: ISystemPower,
        *,
        sound_name: str,
        delay_before_reboot: float = 0.0,
        logger: Optional[Any] = None,
    ):
        self.sound = sound
        self.power = power
        self.sound_name = sound_name
        self.delay = max(0.0, float(delay_before_reboot))
        self.log = logger

    def __call__(self) -> None:
        if self.log:
            try: self.log.info("[LongPress] Playing sound (wait=True) → reboot")
            except Exception: pass
        
        self.sound.play(self.sound_name, wait=True)
        
        if self.delay > 0:
            time.sleep(self.delay)
        self.power.reboot()
