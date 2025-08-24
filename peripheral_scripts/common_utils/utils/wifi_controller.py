#!/usr/bin/env python3
import subprocess

class WifiController:
    def __init__(self, logger=None):
        self.log = logger

    def is_blocked(self) -> bool:
        try:
            result = subprocess.run(
                ['rfkill', 'list', 'wifi'],
                capture_output=True, text=True, check=True, timeout=5
            )
            blocked = 'Soft blocked: yes' in result.stdout
            if self.log:
                self.log.debug("[WifiController] rfkill says wifi is %s", "BLOCKED" if blocked else "UNBLOCKED")
            return blocked
        except subprocess.TimeoutExpired as e:
            if self.log:
                self.log.error("[WifiController] rfkill timeout: %s", e, exc_info=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            if self.log:
                self.log.error("[WifiController] rfkill failed: %s", e, exc_info=True)
            return True

    def set_blocked(self, blocked: bool) -> bool:
        action = 'block' if blocked else 'unblock'
        try:
            subprocess.run(['rfkill', action, 'wifi'], check=True, timeout=5)
            if self.log:
                self.log.info("[WifiController] Wi-Fi %sed successfully.", action)
            return True
        except subprocess.TimeoutExpired as e:
            if self.log:
                self.log.error("[WifiController] rfkill %s timeout: %s", action, e, exc_info=True)
            return False
        except Exception as e:
            if self.log:
                self.log.error("[WifiController] Failed to %s Wi-Fi: %s", action, e, exc_info=True)
            return False
