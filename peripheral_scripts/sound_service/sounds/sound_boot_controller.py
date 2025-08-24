from . import sound_client
from .configs.configs import SOUNDS_LOG_FILE
from utils.logger import setup_logger

log = setup_logger('BootSound', SOUNDS_LOG_FILE)

def main():
    log.info("[BootSound] Sending boot sound command and waiting for completion.")
    ok = sound_client.play_sound('BOOT', wait=True)
    if ok:
        log.info("[BootSound] Command sent and executed successfully.")
    else:
        log.error("[BootSound] Failed to play BOOT sound.")

if __name__ == '__main__':
    main()
