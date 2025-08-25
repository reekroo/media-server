#!/usr/bin/env python3
import subprocess

class InterfaceMonitor:
    def __init__(self, interface_name, logger=None):
        self.interface_name = interface_name
        self.log = logger

    def is_up(self) -> bool:
        try:
            result = subprocess.run(
                ['ip', 'addr', 'show', self.interface_name],
                capture_output=True, text=True, check=True, timeout=5
            )
            up = 'state UP' in result.stdout
            if self.log:
                self.log.debug("[InterfaceMonitor] %s is %s", self.interface_name, "UP" if up else "DOWN")
            return up
        except subprocess.TimeoutExpired as e:
            if self.log:
                self.log.error("[InterfaceMonitor] ip addr timeout: %s", e, exc_info=True)
            return False
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            if self.log:
                self.log.error("[InterfaceMonitor] ip addr failed: %s", e, exc_info=True)
            return False
