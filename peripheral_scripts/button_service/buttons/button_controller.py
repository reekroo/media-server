#!/usr/bin/env python3
from __future__ import annotations

import os
import time
from signal import pause

from .libs.button_actions import ButtonActions
from .configs.settings import load_settings
from buttons.drivers.factory import create_button_by_mode
from .configs.configs import BUTTONS_LOG_FILE

from sounds import sound_client
from utils.logger import setup_logger

log = setup_logger("ButtonController", BUTTONS_LOG_FILE)


class ButtonController:
    """
    Контроллер: читает настройки, создаёт драйвер кнопки (в т.ч. auto),
    применяет доменную логику (cooldown, startup_grace, short/long).
    """

    def __init__(self):
        log.info("[ButtonController] Initializing...")

        self.settings = load_settings()
        self.actions = ButtonActions(logger=log)

        # служебные флаги
        self._started_at = time.monotonic()
        self._press_ts = 0.0
        self._held_fired = False
        self._ignore_until = 0.0
        self._ignore_current_press = False

        # создаём кнопку (внутри — polling+debounce+hold)
        self.button = create_button_by_mode(
            self.settings.mode,
            self.settings.pin,
            self.settings.hold,
            self.settings.bounce,
            logger=log,
        )

        self.button.set_handlers(
            on_press=self._on_press,
            on_release=self._on_release,
            on_hold=self._on_hold,
        )

        log.info(
            "[ButtonController] Button is active (pin=%s, mode=%s, hold=%.2fs, bounce=%.2fs). Waiting for events.",
            self.settings.pin, self.settings.mode, self.settings.hold, self.settings.bounce
        )

    # ===== события =====
    def _on_press(self):
        now = time.monotonic()
        self._press_ts = now
        self._held_fired = False

        # кулдаун после короткого клика — защищает от ложного длинного
        if now < self._ignore_until:
            self._ignore_current_press = True
            log.info("[ButtonController] PRESS edge (ignored by cooldown; is_active=%s)", self.button.is_active())
            return

        self._ignore_current_press = False
        log.info("[ButtonController] PRESS edge (is_active=%s)", self.button.is_active())

    def _on_release(self):
        now = time.monotonic()
        log.info("[ButtonController] RELEASE edge (is_active=%s)", self.button.is_active())

        if self._ignore_current_press:
            self._ignore_current_press = False
            log.debug("[ButtonController] Release of ignored press — no action.")
            return

        if self._held_fired:
            self._held_fired = False
            log.debug("[ButtonController] Short press suppressed after hold.")
            return

        if now - self._started_at < self.settings.startup_grace:
            log.debug("[ButtonController] Suppressing press during startup grace.")
            return

        # короткое нажатие
        log.info("[ButtonController] Short press detected. Sending sound command...")
        sound_client.play_sound(self.settings.sound_short, wait=False)
        self.actions.toggle_wifi()

        # выставим кулдаун (в это окно игнорируем новые press)
        self._ignore_until = now + self.settings.cooldown

    def _on_hold(self):
        # не допускаем hold от "игнорируемого" press (дребезг)
        if self._ignore_current_press:
            log.debug("[ButtonController] Ignoring hold for ignored press session.")
            return

        # подавление первых мгновений после старта
        if time.monotonic() - self._started_at < self.settings.startup_grace:
            log.debug("[ButtonController] Suppressing hold during startup grace.")
            return

        self._held_fired = True
        log.info("[ButtonController] Long press detected. Sending sound command...")
        sound_client.play_sound(self.settings.sound_long, wait=True)
        self.actions.reboot_system()

    # ===== run/close =====
    def run(self):
        pause()

    def close(self):
        log.info("[ButtonController] Closing button controller resources...")
        try:
            self.button.close()
        except Exception:
            pass