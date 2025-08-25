import os

BASE_DIR = os.environ.get("PERIPHERALS_ROOT", "/home/reekroo/peripheral_scripts")
LOG_DIR = os.path.join(BASE_DIR, "logs")
SOUNDS_LOG_FILE = os.path.join(LOG_DIR, "sounds.log")

SOUND_SOCKET = os.environ.get("SOUND_SOCKET", "/tmp/buzzer.sock")