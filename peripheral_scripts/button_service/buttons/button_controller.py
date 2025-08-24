#!/usr/bin/env python3
from gpiozero import Button
from time import monotonic
from signal import pause

from .libs.button_actions import ButtonActions
from .configs import hardware_pins
from .configs.configs import BUTTONS_LOG_FILE, BOUNCE_TIME

from sounds import sound_client
from utils.logger import setup_logger

log = setup_logger('ButtonController', BUTTONS_LOG_FILE)

class ButtonController:
    def __init__(self):
        log.info("[ButtonController] Initializing...")

        self.actions = ButtonActions(logger=log)
        self.button = Button(
            pin=hardware_pins.BUTTON_PIN,
            pull_up=True,
            hold_time=hardware_pins.BUTTON_HOLD_TIME,
            bounce_time=BOUNCE_TIME
        )

        # State to avoid firing short after long
        self._held_fired = False
        self._press_t = 0.0

        self.button.when_pressed = self._on_press
        self.button.when_released = self._on_release
        self.button.when_held = self._on_held

        log.info("[ButtonController] Button is active and waiting for events.")

    def _on_press(self):
        self._press_t = monotonic()
        self._held_fired = False

    def _on_held(self):
        self._held_fired = True
        log.info("[ButtonController] Long press detected. Sending sound command...")
        sound_client.play_sound('REBOOT_SYSTEM')
        self.actions.reboot_system()

    def _on_release(self):
        # Skip short action if long press was already handled
        if self._held_fired:
            self._held_fired = False
            return

        log.info("[ButtonController] Short press detected. Sending sound command...")
        sound_client.play_sound('WIFI_TOGGLE')
        self.actions.toggle_wifi()

    def run(self):
        pause()

    def close(self):
        log.info("[ButtonController] Closing button controller resources...")
