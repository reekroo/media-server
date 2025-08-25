#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from typing import Optional, Any
from ..ports.wifi_port import IWifi

class RfkillWifiAdapter(IWifi):
    
    def __init__(self, logger: Optional[Any] = None):
        self.log = logger

    def _is_soft_blocked(self) -> bool:
        try:
            out = subprocess.check_output(["rfkill", "list", "wifi"], text=True, stderr=subprocess.DEVNULL)
            for line in out.splitlines():
                line = line.strip().lower()
                if line.startswith("soft blocked:"):
                    return "yes" in line
        except Exception:
            if self.log:
                try: self.log.warning("[WifiAdapter] Can't read rfkill state; assuming unblocked")
                except Exception: pass
        return False

    def enable(self) -> None:
        if self.log:
            try: self.log.info("[ButtonActions] Turning on Wi-Fi...")
            except Exception: pass
        subprocess.run(["rfkill", "unblock", "wifi"], check=False)
        if self.log:
            try: self.log.info("[ButtonActions] Wi-Fi toggle complete.")
            except Exception: pass

    def disable(self) -> None:
        if self.log:
            try: self.log.info("[ButtonActions] Turning off Wi-Fi...")
            except Exception: pass
        subprocess.run(["rfkill", "block", "wifi"], check=False)
        if self.log:
            try: self.log.info("[ButtonActions] Wi-Fi toggle complete.")
            except Exception: pass

    def toggle(self) -> None:
        if self._is_soft_blocked():
            self.enable()
        else:
            self.disable()
