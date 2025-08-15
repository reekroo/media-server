#!/usr/bin/env python3

from gpiozero import Button
from signal import pause
import sys

sys.path.append('/home/reekroo/scripts')

from buttons.libs.button_actions import ButtonActions
from sounds import sound_client
from common.logger import setup_logger

log = setup_logger('ButtonController', '/home/reekroo/scripts/logs/buttons.log')

class ButtonController:
    def __init__(self, pin=23, hold_time=3):
        log.info("[ButtonController] Initializing...")
        self.actions = ButtonActions(logger=log)
        self.button = Button(pin, pull_up=True, hold_time=hold_time)

        self.button.when_released = self.handle_short_press
        self.button.when_held = self.handle_long_press

        log.info("[ButtonController] Button is active and waiting for events.")

    def handle_short_press(self):
        log.info("Short press detected. Sending sound command...")
        sound_client.play_sound('WIFI_TOGGLE')

        self.actions.toggle_wifi()

    def handle_long_press(self):
        log.info("Long press detected. Sending sound command...")
        sound_client.play_sound('REBOOT_SYSTEM')

        self.actions.reboot_system()

    def run(self):
        pause()

    def close(self):
        log.info("[ButtonController] Closing button controller resources...")

if __name__ == '__main__':
    controller = ButtonController()
    try:
        controller.run()
    except KeyboardInterrupt:
        log.info("[ButtonController] stopped by user.")
    finally:
        controller.close()