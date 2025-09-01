import os

BASE_DIR = os.environ.get("PERIPHERALS_ROOT", "/home/reekroo/peripheral_scripts")
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "bluetooth_policy.log")

BT_BLOCK_METHOD = os.environ.get("BT_BLOCK_METHOD", "rfkill")   # rfkill|bluetoothctl|hciconfig
BT_DEVICE = os.environ.get("BT_DEVICE", "hci0")                 # hciconfig/bluetoothctl
