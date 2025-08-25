#!/usr/bin/env python3
from __future__ import annotations

import threading
import time
from typing import Callable, Optional, Union

from gpiozero import DigitalInputDevice


class BaseButton:
    """
    Обёртка над gpiozero.DigitalInputDevice с *собственным опросом* (polling):
      - работаем с внешними модулями (pull_up=None) и явной полярностью (active_high).
      - дребезг реализуем по времени (bounce_time).
      - long-press делаем через таймер (hold_time).
    """

    def __init__(
        self,
        *,
        pin: int,
        hold_time: float,
        bounce_time: float,
        pull_up: Optional[bool],   # None | True | False
        active_high: bool,         # True -> нажатие = HIGH, False -> нажатие = LOW
        poll_interval: float = 0.01,
    ):
        # Важно: фабрика lgpio задаётся через env (GPIOZERO_PIN_FACTORY=lgpio)
        self._dev = DigitalInputDevice(
            pin=pin,
            pull_up=pull_up,
            active_state=active_high,
            bounce_time=None,     # дебаунсим сами
        )

        self._hold_time: float = max(0.0, float(hold_time))
        self._bounce_time: float = max(0.0, float(bounce_time))
        self._poll_interval: float = max(0.002, float(poll_interval))  # 2ms..∞

        self._on_press: Optional[Callable] = None
        self._on_release: Optional[Callable] = None
        self._on_hold: Optional[Callable] = None

        self._press_ts: float = 0.0
        self._held_fired: bool = False

        self._last_state: bool = bool(self._dev.is_active)
        self._last_change_ts: float = time.monotonic()

        self._hold_timer: Optional[threading.Timer] = None
        self._stop_evt = threading.Event()
        self._thread = threading.Thread(target=self._poll_loop, name="ButtonPoll", daemon=True)
        self._thread.start()

    # ---------- публичный API ----------
    def set_handlers(
        self,
        on_press: Optional[Callable] = None,
        on_release: Optional[Callable] = None,
        on_hold: Optional[Callable] = None,
    ):
        self._on_press = on_press
        self._on_release = on_release
        self._on_hold = on_hold

    def is_active(self) -> bool:
        return bool(self._dev.is_active)

    @property
    def raw(self) -> DigitalInputDevice:
        return self._dev

    def close(self) -> None:
        # остановим опрос
        try:
            self._stop_evt.set()
            if self._thread.is_alive():
                self._thread.join(timeout=0.5)
        except Exception:
            pass

        # отменим таймер удержания
        try:
            if self._hold_timer:
                self._hold_timer.cancel()
        except Exception:
            pass
        finally:
            self._hold_timer = None

        # закроем девайс
        try:
            self._dev.close()
        except Exception:
            pass

    # ---------- внутренняя логика ----------
    def _poll_loop(self):
        # опрашиваем линию и детектим фронты с программным дебаунсом
        while not self._stop_evt.is_set():
            now = time.monotonic()
            cur = bool(self._dev.is_active)

            if cur != self._last_state:
                # проверка на дебаунс по времени
                if (now - self._last_change_ts) >= self._bounce_time:
                    self._last_state = cur
                    self._last_change_ts = now
                    if cur:
                        self._handle_press()
                    else:
                        self._handle_release()

            time.sleep(self._poll_interval)

    def _handle_press(self):
        self._held_fired = False
        self._press_ts = time.monotonic()

        # стартуем таймер удержания
        if self._hold_time > 0:
            try:
                if self._hold_timer:
                    self._hold_timer.cancel()
            except Exception:
                pass
            self._hold_timer = threading.Timer(self._hold_time, self._fire_hold_if_still_active)
            self._hold_timer.daemon = True
            self._hold_timer.start()

        if self._on_press:
            try:
                self._on_press()
            except Exception:
                pass

    def _handle_release(self):
        # отменяем таймер удержания
        try:
            if self._hold_timer:
                self._hold_timer.cancel()
        except Exception:
            pass
        finally:
            self._hold_timer = None

        if self._on_release:
            try:
                self._on_release()
            except Exception:
                pass

    def _fire_hold_if_still_active(self):
        # по истечении hold_time проверим, всё ли ещё активен
        try:
            if self._dev.is_active and not self._held_fired:
                self._held_fired = True
                if self._on_hold:
                    self._on_hold()
        except Exception:
            pass
