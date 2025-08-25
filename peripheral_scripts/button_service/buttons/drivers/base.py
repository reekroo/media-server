#!/usr/bin/env python3
from __future__ import annotations

import threading
import time
from typing import Callable, Optional

from gpiozero import DigitalInputDevice


class BaseButton:
    def __init__(
        self,
        *,
        pin: int,
        pull_up: Optional[bool],
        active_high: bool,
        bounce_time: float,
        hold_time: float,
        poll_interval: float = 0.01,
    ):
        self._dev = DigitalInputDevice(
            pin=pin,
            pull_up=pull_up,
            active_state=active_high,
            bounce_time=None,
        )

        self._bounce = max(0.0, float(bounce_time))
        self._hold = max(0.0, float(hold_time))
        self._poll = max(0.002, float(poll_interval))

        self._on_press: Optional[Callable[[], None]] = None
        self._on_release: Optional[Callable[[], None]] = None
        self._on_hold: Optional[Callable[[], None]] = None

        self._last_state: bool = bool(self._dev.is_active)
        self._last_change_ts: float = time.monotonic()

        self._hold_timer: Optional[threading.Timer] = None
        self._stop_evt = threading.Event()
        self._thread = threading.Thread(target=self._poll_loop, name="ButtonPoll", daemon=True)
        self._thread.start()

    def set_handlers(
        self,
        *,
        on_press: Optional[Callable[[], None]] = None,
        on_release: Optional[Callable[[], None]] = None,
        on_hold: Optional[Callable[[], None]] = None,
    ) -> None:
        self._on_press = on_press
        self._on_release = on_release
        self._on_hold = on_hold

    def is_active(self) -> bool:
        return bool(self._dev.is_active)

    def close(self) -> None:
        try:
            self._stop_evt.set()
            if self._thread.is_alive():
                self._thread.join(timeout=0.5)
        except Exception:
            pass
        try:
            if self._hold_timer:
                self._hold_timer.cancel()
        except Exception:
            pass
        try:
            self._dev.close()
        except Exception:
            pass

    def _poll_loop(self) -> None:
        while not self._stop_evt.is_set():
            now = time.monotonic()
            cur = bool(self._dev.is_active)

            if cur != self._last_state and (now - self._last_change_ts) >= self._bounce:
                self._last_state = cur
                self._last_change_ts = now
                if cur:
                    self._on_press_edge()
                else:
                    self._on_release_edge()

            time.sleep(self._poll)

    def _on_press_edge(self) -> None:
        if self._hold > 0:
            try:
                if self._hold_timer:
                    self._hold_timer.cancel()
            except Exception:
                pass
            self._hold_timer = threading.Timer(self._hold, self._maybe_fire_hold)
            self._hold_timer.daemon = True
            self._hold_timer.start()

        if self._on_press:
            try:
                self._on_press()
            except Exception:
                pass

    def _on_release_edge(self) -> None:
        try:
            if self._hold_timer:
                self._hold_timer.cancel()
        except Exception:
            pass
        self._hold_timer = None

        if self._on_release:
            try:
                self._on_release()
            except Exception:
                pass

    def _maybe_fire_hold(self) -> None:
        try:
            if self._dev.is_active and self._on_hold:
                self._on_hold()
        except Exception:
            pass
