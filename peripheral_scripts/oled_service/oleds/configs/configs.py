import os

BASE_DIR = os.environ.get("PERIPHERALS_ROOT", "/home/reekroo/peripheral_scripts")
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "oleds.log")

# Rendering / UI
PAGE_INTERVAL = int(os.environ.get("OLED_PAGE_INTERVAL", "10"))     # seconds per page
UPDATE_INTERVAL = int(os.environ.get("OLED_UPDATE_INTERVAL", "2"))  # refresh period

# Font configuration
FONT_PATH = os.environ.get("OLED_FONT_PATH", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
FONT_SIZE = int(os.environ.get("OLED_FONT_SIZE", "10"))

# Weather socket
WEATHER_SERVICE_SOCKET = os.environ.get("WEATHER_SERVICE_SOCKET", "/tmp/weather_service.sock")