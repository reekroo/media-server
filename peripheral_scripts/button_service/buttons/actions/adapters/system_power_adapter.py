#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from typing import Optional, Any
from ..ports.system_port import ISystemPower

class SystemPowerAdapter(ISystemPower):
    def __init__(self, logger: Optional[Any] = None):
        self.log = logger

    def reboot(self) -> None:
        if self.log:
            try: self.log.warning("[ButtonActions] LONG PRESS DETECTED. Issuing reboot command.")
            except Exception: pass

        subprocess.Popen(["/sbin/reboot"])
