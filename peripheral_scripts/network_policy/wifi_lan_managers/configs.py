import os

BASE_DIR = os.environ.get("PERIPHERALS_ROOT", "/home/reekroo/peripheral_scripts")
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "network_policy.log"),

LAN_INTERFACE = os.environ.get("LAN_INTERFACE", "eth0")
AUTO_UNBLOCK_WHEN_LAN_DOWN = os.environ.get("AUTO_UNBLOCK_WHEN_LAN_DOWN", "0") in ("1", "true", "True")
