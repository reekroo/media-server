#!/usr/bin/env python3

import sys

sys.path.append('/home/reekroo/scripts')
from sounds.libs.buzzer_player import BuzzerPlayer
from sounds.configs import melodies
from common.logger import setup_logger

log = setup_logger('BootSound', '/home/reekroo/scripts/logs/sounds.log')

def main():
    log.info("[BootSound] Boot sound service started.")
    player = None
    try:
        player = BuzzerPlayer()
        player.play(melodies.BOOT)
        log.info("[BootSound] Boot sound played successfully.")
    except Exception as e:
        log.error(f"[BootSound] Failed to play boot sound: {e}", exc_info=True)
    finally:
        if player:
            player.close()
        log.info("[BootSound] Boot sound service finished.")

if __name__ == '__main__':
    main()