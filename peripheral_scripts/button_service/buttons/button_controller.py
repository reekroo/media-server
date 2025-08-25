#!/usr/bin/env python3
from __future__ import annotations

import os
import time
from signal import pause

from .libs.button_actions import ButtonActions
from .configs.settings import load_settings
from .drivers.factory import create_button_by_mode
from .configs.configs import BUTTONS_LOG_FILE

from sounds import sound_client
from utils.logger import setup_logger

log = setup_logger("ButtonController", BUTTONS_LOG_FILE)


class ButtonController:
    def __init__(self):
        log.info("[ButtonController] Initializing...")

        self.settings = load_settings()
        self.actions = ButtonActions(logger=log)

        # доп. настройки с дефолтами: можем прокинуть через env
        self.cooldown_after_press = float(
            getattr(self.settings, "cooldown", os.getenv("BUTTON_COOLDOWN", "0.8"))
        )
        self.startup_grace = float(
            getattr(self.settings, "startup_grace", os.getenv("BUTTON_STARTUP_GRACE", "0.8"))
        )

        self._started_at = time.monotonic()
        self._held_fired = False
        self._press_ts = 0.0

        # антидребезговые доп. флаги
        self._ignore_until = 0.0          # время, до которого игнорируем новые PRESSES
        self._ignore_current_press = False  # игнорировать ли именно эту «сессию» нажатия

        # создаём кнопку согласно режиму/пину/временам (внутри — опрос с дебаунсом)
        self.button = create_button_by_mode(
            self.settings.mode,
            self.settings.pin,
            self.settings.hold,
            self.settings.bounce,
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

    # ==== события ====
    def _on_press(self):
        now = time.monotonic()
        self._held_fired = False
        self._press_ts = now

        # если ещё в кулдауне после предыдущего короткого нажатия — игнорируем этот press
        if now < self._ignore_until:
            self._ignore_current_press = True
            log.info("[ButtonController] PRESS edge (ignored by cooldown; is_active=%s)", self.button.is_active())
            return

        self._ignore_current_press = False
        log.info("[ButtonController] PRESS edge (is_active=%s)", self.button.is_active())

    def _on_release(self):
        now = time.monotonic()
        log.info("[ButtonController] RELEASE edge (is_active=%s)", self.button.is_active())

        # если этот press был игнорирован (дребезг/повтор) — просто сбрасываем флаг
        if self._ignore_current_press:
            self._ignore_current_press = False
            log.debug("[ButtonController] Release of ignored press — no action.")
            return

        # если уже сработал hold — не считаем это коротким нажатием
        if self._held_fired:
            self._held_fired = False
            log.debug("[ButtonController] Short press suppressed after hold.")
            return

        # подавим ложные нажатия в первые секунды после старта
        if now - self._started_at < self.startup_grace:
            log.debug("[ButtonController] Suppressing press during startup grace.")
            return

        # КОРОТКОЕ НАЖАТИЕ
        log.info("[ButtonController] Short press detected. Sending sound command...")
        sound_client.play_sound(self.settings.sound_short, wait=False)
        self.actions.toggle_wifi()

        # выставим кулдаун, чтобы следующее ложное «PRESS» за дребезг не привело к hold
        self._ignore_until = now + self.cooldown_after_press

    def _on_hold(self):
        # если текущий «PRESS» уже помечен как игнорируемый — глушим hold
        if self._ignore_current_press:
            log.debug("[ButtonController] Ignoring hold for ignored press session.")
            return

        # подавим во время стартового грейса
        if time.monotonic() - self._started_at < self.startup_grace:
            log.debug("[ButtonController] Suppressing hold during startup grace.")
            return

        self._held_fired = True
        log.info("[ButtonController] Long press detected. Sending sound command...")
        sound_client.play_sound(self.settings.sound_long, wait=True)
        self.actions.reboot_system()

    # ==== run / close ====
    def run(self):
        pause()

    def close(self):
        log.info("[ButtonController] Closing button controller resources...")
        try:
            self.button.close()
        except Exception:
            pass
