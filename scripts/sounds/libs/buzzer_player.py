#!/usr/bin/env python3

from gpiozero import TonalBuzzer
from time import sleep

class BuzzerPlayer:

    def __init__(self, pin=18):
        self.bz = TonalBuzzer(pin)
        self.is_playing = False

    def play(self, melody):
        if self.is_playing:
            print("Buzzer is already busy.")
            return

        self.is_playing = True
        try:
            for note, duration in melody:
                if note is None:
                    sleep(duration)
                else:
                    self.bz.play(note)
                    sleep(duration)
                    self.bz.stop()
                    sleep(0.06)
        finally:
            self.bz.stop()
            sleep(0.06)
            self.is_playing = False

    def close(self):
        self.bz.close()
        sleep(0.06)