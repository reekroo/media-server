from . import sound_client
from utils.logger import setup_logger
from .configs.configs import SOUNDS_LOG_FILE

log = setup_logger('ShutdownSound', SOUNDS_LOG_FILE)

def main():
    log.info("[ShutdownSound] Sending shutdown sound command to sound service and waiting for completion.")
    ok = sound_client.play_sound('SHUTDOWN', wait=True)
    if ok:
        log.info("[ShutdownSound] Command sent and executed successfully.")
    else:
        log.error("[ShutdownSound] Failed to play SHUTDOWN sound.")

if __name__ == '__main__':
    main()
