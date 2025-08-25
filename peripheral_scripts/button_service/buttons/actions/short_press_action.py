#!/usr/bin/env python3
from __future__ import annotations

from typing import Optional, Any
from .ports.sound_port import ISound
from .ports.wifi_port import IWifi

class ShortPressAction:

    def __init__(self, sound: ISound, wifi: IWifi, *, sound_name: str, logger: Optional[Any] = None):
        self.sound = sound
        self.wifi = wifi
        self.sound_name = sound_name
        self.log = logger

    def __call__(self) -> None:
        if self.log:
            try: self.log.info("[ShortPress] Sending sound and toggling Wi-Fi...")
            except Exception: pass
            
        self.sound.play(self.sound_name, wait=False)
        self.wifi.toggle()
