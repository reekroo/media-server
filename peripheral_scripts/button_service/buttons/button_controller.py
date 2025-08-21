#!/usr/bin/env python3

from gpiozero import Button
from signal import pause

from buttons.libs.button_actions import ButtonActions
from buttons.configs import hardware_pins

from sounds import sound_client
from utils.logger import setup_logger

log = setup_logger('ButtonController', '/home/reekroo/scripts/logs/buttons.log')

class ButtonController:
    def __init__(self):
        log.info("[ButtonController] Initializing...")
        
        self.actions = ButtonActions(logger=log)
        self.button = Button(
            pin=hardware_pins.BUTTON_PIN, 
            pull_up=True, 
            hold_time=hardware_pins.BUTTON_HOLD_TIME
        )
        
        self.button.when_released = self.handle_short_press
        self.button.when_held = self.handle_long_press

        log.info("[ButtonController] Button is active and waiting for events.")

    def handle_short_press(self):
        log.info("[ButtonController] Short press detected. Sending sound command...")
        sound_client.play_sound('WIFI_TOGGLE')

        self.actions.toggle_wifi()

    def handle_long_press(self):
        log.info("[ButtonController] Long press detected. Sending sound command...")
        sound_client.play_sound('REBOOT_SYSTEM')

        self.actions.reboot_system()

    def run(self):
        pause()

    def close(self):
        log.info("[ButtonController] Closing button controller resources...")