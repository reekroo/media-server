#!/usr/bin/env python3

import subprocess

class ButtonActions:
    def __init__(self, logger):
        self.log = logger
        self.busy = False

    def toggle_wifi(self):
        if self.busy:
            self.log.warning("[ButtonActions] Action is busy, ignoring toggle.")
            return
        
        self.busy = True
        try:
            result = subprocess.run(['rfkill', 'list', 'wifi'], capture_output=True, text=True, check=True)

            if "Soft blocked: yes" in result.stdout:
                self.log.info("[ButtonActions] Turning on Wi-Fi...")
                subprocess.run(["rfkill", "unblock", "wifi"], check=True)
            else:
                self.log.info("[ButtonActions] Turning off Wi-Fi...")
                subprocess.run(["rfkill", "block", "wifi"], check=True)
            
            self.log.info("[ButtonActions] Wi-Fi toggle complete.")

        except Exception as e:
            self.log.error(f"[ButtonActions] Error toggling Wi-Fi: {e}", exc_info=True)
        finally:
            self.busy = False

    def reboot_system(self):
        self.log.warning("[ButtonActions] LONG PRESS DETECTED. Issuing reboot command.")
        try:
            subprocess.run(["shutdown", "-r", "now"], check=True)
        except Exception as e:
            self.log.error(f"[ButtonActions] Error issuing reboot command: {e}", exc_info=True)