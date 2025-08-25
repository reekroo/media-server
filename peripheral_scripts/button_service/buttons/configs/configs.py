import os

BASE_DIR = os.environ.get("PERIPHERALS_ROOT", "/home/reekroo/peripheral_scripts")
LOG_DIR = os.path.join(BASE_DIR, "logs")
BUTTONS_LOG_FILE = os.path.join(LOG_DIR, "buttons.log")

BOUNCE_TIME = float(os.environ.get("BUTTON_BOUNCE_TIME", "0.2"))
