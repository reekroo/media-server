#!/usr/bin/env python3

import sys
sys.path.append('/home/reekroo/scripts')

from sounds import sound_client
from common.logger import setup_logger

log = setup_logger('BootSound', '/home/reekroo/scripts/logs/sounds.log')

def main():
    log.info("[BootSound] Sending boot sound command and waiting for completion.")

    try:
        sound_client.play_sound('BOOT', wait=True)
        log.info("[BootSound] Command sent and executed successfully.")
    
    except Exception as e:
        log.error(f"[BootSound] Failed to send command: {e}", exc_info=True)

if __name__ == '__main__':
    main()