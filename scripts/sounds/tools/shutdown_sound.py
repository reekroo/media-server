#!/usr/bin/env python3

import sys

sys.path.append('/home/reekroo/scripts')

from sounds import sound_client
from common.logger import setup_logger

log = setup_logger('ShutdownSound', '/home/reekroo/scripts/logs/sounds.log')

def main():
    log.info("[ShutdownSound] Sending shutdown sound command to sound service.")
    try:
        sound_client.play_sound('SHUTDOWN')
        log.info("[ShutdownSound] Command sent successfully.")
    except Exception as e:
        log.error(f"[ShutdownSound] Failed to send command: {e}", exc_info=True)

if __name__ == '__main__':
    main()