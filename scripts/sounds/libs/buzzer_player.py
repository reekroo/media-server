#!/usr/bin/env python3

from gpiozero.pins.lgpio import LGPIOFactory
from gpiozero import Device, TonalBuzzer
Device.pin_factory = LGPIOFactory()

import threading
import time

from sounds.configs import hardware_pins

class BuzzerPlayer:
    def __init__(self):
        self.pin = hardware_pins.BUZZER_PIN
        self._thread = None
        self._lock = threading.Lock()

    def _play_task(self, buzzer_instance, melody, duration_seconds, stop_event):
        try:
            start_time = time.time()
            is_looping = duration_seconds > 0

            while not stop_event.is_set():
                if is_looping and (time.time() - start_time) >= duration_seconds:
                    break
                
                for note, duration in melody:
                    if stop_event.is_set():
                        break
                    if note:
                        buzzer_instance.play(note)

                    if stop_event.wait(duration):
                        break

                    buzzer_instance.stop()
                    
                    if stop_event.wait(0.06):
                        break

                if not is_looping:
                    break
        finally:
            buzzer_instance.close()

    def play(self, melody, duration_seconds=0):
        with self._lock:
            if self._thread and self._thread.is_alive():
                self._thread.stop_event.set()
                self._thread.join()

            local_buzzer = TonalBuzzer(self.pin)

            stop_event = threading.Event()

            self._thread = threading.Thread(
                target=self._play_task, 
                args=(local_buzzer, melody, duration_seconds, stop_event)
            )
            self._thread.stop_event = stop_event
            self._thread.start()

    def stop(self):
        with self._lock:
            if self._thread and self._thread.is_alive():
                self._thread.stop_event.set()
                self._thread.join()
    
    def close(self):
        self.stop()