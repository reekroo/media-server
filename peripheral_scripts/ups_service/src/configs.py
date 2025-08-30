import os
import os.path as p

BASE_DIR = os.environ.get("PERIPHERALS_ROOT", "/home/reekroo/peripheral_scripts")
LOG_DIR = p.join(BASE_DIR, "logs")
UPS_LOG_FILE = p.join(LOG_DIR, "ups.log")

RUN_ROOT = os.environ.get("PERIPHERALS_RUN_ROOT", "/run/peripherals")
UPS_STATE_DIR = p.join(RUN_ROOT, "ups")
UPS_STATUS_PATH = p.join(UPS_STATE_DIR, "status.json")

I2C_BUS = int(os.environ.get("UPS_I2C_BUS", "1"))
I2C_ADDR = int(os.environ.get("UPS_I2C_ADDR", "0x36"), 16)

GPIO_AC_PIN = int(os.environ.get("UPS_GPIO_AC_PIN", "6"))
AC_ACTIVE_HIGH = os.environ.get("UPS_AC_ACTIVE_HIGH", "1") == "1"

POLL_INTERVAL_SEC = float(os.environ.get("UPS_POLL_INTERVAL_SEC", "5"))
LOW_BATTERY_PERCENT = float(os.environ.get("UPS_LOW_BATTERY_PERCENT", "10"))
LOW_BATT_DEBOUNCE_SEC = float(os.environ.get("UPS_LOW_BATT_DEBOUNCE_SEC", "60"))

DRY_RUN = os.environ.get("UPS_DRY_RUN", "0") == "1"
SHUTDOWN_CMD = tuple(os.environ.get(
    "UPS_SHUTDOWN_CMD",
    "/sbin/shutdown -h now 'UPS: battery critically low'"
).split())