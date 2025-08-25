#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path

from utils.logger import setup_logger
from .button_controller import ButtonController
from .configs.settings import load_settings
from .drivers.factory import create_button_by_mode
from .configs.configs import BUTTONS_LOG_FILE

from .actions.adapters.sound_adapter import SoundClientAdapter
from .actions.adapters.wifi_adapter import RfkillWifiAdapter
from .actions.adapters.system_power_adapter import SystemPowerAdapter
from .actions.short_press_action import ShortPressAction
from .actions.long_press_action import LongPressAction

log = setup_logger("ButtonController", BUTTONS_LOG_FILE)

def main() -> None:
    settings = load_settings()

    button = create_button_by_mode(
        settings.mode,
        settings.pin,
        settings.hold,
        settings.bounce,
        logger=log,
    )

    sound = SoundClientAdapter(logger=log)
    wifi = RfkillWifiAdapter(logger=log)
    power = SystemPowerAdapter(logger=log)

    short_uc = ShortPressAction(sound, wifi, sound_name=settings.sound_short, logger=log)
    long_uc  = LongPressAction(sound, power, sound_name=settings.sound_long, delay_before_reboot=0.0, logger=log)

    controller = ButtonController(
        button=button,
        settings=settings,
        log=log,
        short_action=short_uc,
        long_action=long_uc,
    )
    controller.run()


if __name__ == "__main__":
    main()
