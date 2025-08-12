#!/usr/bin/env python3

import subprocess
import threading

class ButtonActions:
    def __init__(self, logger, player, melodies):
        self.log = logger
        self.player = player
        self.melodies = melodies
        self.busy = False

    def _play_sound_in_background(self, melody):
        sound_thread = threading.Thread(target=self.player.play, args=(melody,))
        sound_thread.start()

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
                self.player.play(self.melodies.WIFI_ON)
            else:
                self.log.info("[ButtonActions] Turning off Wi-Fi...")
                subprocess.run(["rfkill", "block", "wifi"], check=True)
                self.player.play(self.melodies.WIFI_OFF)
            
            self.log.info("[ButtonActions] Wi-Fi toggle complete.")

        except Exception as e:
            self.log.error(f"[ButtonActions] Error toggling Wi-Fi: {e}", exc_info=True)
            self.player.play(self.melodies.FAILURE)
        finally:
            self.busy = False

    def reboot_system(self):
        self.log.warning("[ButtonActions] LONG PRESS DETECTED. Issuing shutdown command.")
        subprocess.run(["shutdown", "-r", "now"], check=True)

    def close(self):
        self.player.close()