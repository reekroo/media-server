#!/usr/bin/env python3

import sys
sys.path.append('/home/reekroo/peripheral_scripts')

from sounds import sound_client
from common_utils.logger import setup_logger

log = setup_logger('ShutdownSound', '/home/reekroo/peripheral_scripts/logs/sounds.log')

def main():
    log.info("[ShutdownSound] Sending shutdown sound command to sound service and waiting for completion.")
    
    try:
        sound_client.play_sound('SHUTDOWN', wait=True)
        log.info("[ShutdownSound] Command sent and executed successfully.")

    except Exception as e:
        log.error(f"[ShutdownSound] Failed to send command: {e}", exc_info=True)

if __name__ == '__main__':
    main()