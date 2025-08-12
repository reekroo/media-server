#!/usr/bin/env python3

from time import sleep
from buzzer_player import BuzzerPlayer

import melodies

def main():
    print("--- Running BuzzerPlayer Tests ---")

    player = BuzzerPlayer()

    print("\nPlaying BOOT melody...")
    player.play(melodies.BOOT)
    sleep(1)

    print("\nPlaying SHUTDOWN melody...")
    player.play(melodies.SHUTDOWN)
    sleep(1)

    print("\nPlaying SUCCESS melody...")
    player.play(melodies.SUCCESS)
    sleep(1)

    print("\nPlaying FAILURE melody...")
    player.play(melodies.FAILURE)
    sleep(1)

    player.close()

    print("\n--- All sound tests complete. ---")

if __name__ == '__main__':
    main()