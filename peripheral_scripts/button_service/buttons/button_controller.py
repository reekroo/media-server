#!/usr/bin/env python3
from __future__ import annotations

import time
from typing import Any, Callable

class ButtonController:
    def __init__(
        self,
        *,
        button,
        settings,
        log: Any,
        short_action: Callable[[], None],
        long_action: Callable[[], None],
    ):
        self.log = log
        self.settings = settings
        self.button = button
        self.short_action = short_action
        self.long_action = long_action

        self._started_at = time.monotonic()
        self._press_ts = 0.0
        self._held_fired = False
        self._ignore_until = 0.0
        self._ignore_current_press = False

        self.button.set_handlers(
            on_press=self._on_press,
            on_release=self._on_release,
            on_hold=self._on_hold,
        )

        self.log.info(
            "[ButtonController] Button is active (pin=%s, mode=%s, hold=%.2fs, bounce=%.2fs). Waiting for events.",
            self.settings.pin, self.settings.mode, self.settings.hold, self.settings.bounce
        )

    def _on_press(self):
        now = time.monotonic()
        self._press_ts = now
        self._held_fired = False

        if now < self._ignore_until:
            self._ignore_current_press = True
            self.log.info(
                "[ButtonController] PRESS edge (ignored by cooldown; is_active=%s)",
                self.button.is_active()
            )
            return

        self._ignore_current_press = False
        self.log.info("[ButtonController] PRESS edge (is_active=%s)", self.button.is_active())

    def _on_release(self):
        now = time.monotonic()
        self.log.info("[ButtonController] RELEASE edge (is_active=%s)", self.button.is_active())

        if self._ignore_current_press:
            self._ignore_current_press = False
            self.log.debug("[ButtonController] Release of ignored press — no action.")
            return

        if self._held_fired:
            self._held_fired = False
            self.log.debug("[ButtonController] Short press suppressed after hold.")
            return

        if now - self._started_at < self.settings.startup_grace:
            self.log.debug("[ButtonController] Suppressing press during startup grace.")
            return

        self.log.info("[ButtonController] Short press detected.")
        try:
            self.short_action()
        finally:
            self._ignore_until = now + self.settings.cooldown

    def _on_hold(self):
        if self._ignore_current_press:
            self.log.debug("[ButtonController] Ignoring hold for ignored press session.")
            return
        if time.monotonic() - self._started_at < self.settings.startup_grace:
            self.log.debug("[ButtonController] Suppressing hold during startup grace.")
            return

        self._held_fired = True
        self.log.info("[ButtonController] Long press detected.")
        self.long_action()

    def run(self):
        from signal import pause
        pause()

    def close(self):
        self.log.info("[ButtonController] Closing button controller resources...")
        try:
            self.button.close()
        except Exception:
            pass