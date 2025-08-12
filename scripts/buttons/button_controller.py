#!/usr/bin/env python3

from gpiozero import Button
from signal import pause
import sys

sys.path.append('/home/reekroo/scripts')
from buttons.libs.button_actions import ButtonActions
from sounds.libs.buzzer_player import BuzzerPlayer
from sounds.configs import melodies
from common.logger import setup_logger

log = setup_logger('ButtonController', '/home/reekroo/scripts/logs/buttons.log')
player = BuzzerPlayer()

class ButtonController:
    def __init__(self, pin=23, hold_time=3):        
        log.info("[ButtonController] Initializing...")
        self.actions = ButtonActions(logger=log, player=player, melodies=melodies)
        self.button = Button(pin, pull_up=True, hold_time=hold_time)
        self.button.when_released = self.actions.toggle_wifi
        self.button.when_held = self.actions.reboot_system
        log.info("[ButtonController] Button is active and waiting for events.")

    def run(self):
        pause()

    def close(self):
        log.info("[ButtonController] Closing button controller resources...")
        self.actions.close()

if __name__ == '__main__':
    controller = ButtonController()
    try:
        controller.run()
    except KeyboardInterrupt:
        log.info("[ButtonController] stopped by user.")
    finally:
        controller.close()