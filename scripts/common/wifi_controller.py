#!/usr/bin/env python3

import subprocess

class WifiController:
    def is_blocked(self):
        try:
            result = subprocess.run(
                ['rfkill', 'list', 'wifi'],
                capture_output=True, text=True, check=True
            )
            return 'Soft blocked: yes' in result.stdout
        except (subprocess.CalledProcessError, FileNotFoundError):
            return True

    def set_blocked(self, blocked):
        action = 'block' if blocked else 'unblock'
        print(f"WifiController: Setting Wi-Fi to '{action}'...")
        try:
            subprocess.run(['rfkill', action, 'wifi'], check=True)
            print("WifiController: Done.")
        except Exception as e:
            print(f"WifiController: Failed to {action} Wi-Fi: {e}")
