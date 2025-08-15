#!/usr/bin/env python3

from gpiozero import TonalBuzzer
from time import sleep
import threading
import time

class BuzzerPlayer:
    def __init__(self, pin=18):
        self.bz = TonalBuzzer(pin)
        self._thread = None
        self._lock = threading.Lock()

    def _play_task(self, melody, duration_seconds, stop_event):
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
                        self.bz.play(note)
                    
                    stop_event.wait(duration)
                    self.bz.stop()
                    sleep(0.06)

                if not is_looping:
                    break
        finally:
            self.bz.stop()
            sleep(0.06)

    def play(self, melody, duration_seconds=0):
        with self._lock:
            if self._thread and self._thread.is_alive():
                self._thread.stop_event.set()
                self._thread.join()

            stop_event = threading.Event()
            self._thread = threading.Thread(target=self._play_task, args=(melody, duration_seconds, stop_event))
            self._thread.stop_event = stop_event
            self._thread.start()

    def stop(self):
        with self._lock:
            if self._thread and self._thread.is_alive():
                self._thread.stop_event.set()
                self._thread.join()
            self.bz.stop()
            sleep(0.06)

    def close(self):
        self.stop()
        self.bz.close()