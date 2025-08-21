#!/usr/bin/env python3

from PIL import Image, ImageDraw, ImageFont
from ..configs.oled_icons import ICON_DATA

class DisplayManager:
    def __init__(self, driver):
        self.driver = driver
        self.width = self.driver.width
        self.height = self.driver.height
        self.image = Image.new("1", (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)
        try:
            self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
        except IOError:
            self.font = ImageFont.load_default()
        
        self.icons = {name: Image.frombytes('1', (8, 8), bytes(data)) for name, data in ICON_DATA.items()}

    def clear(self):
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

    def show(self):
        self.driver.show(self.image)

    def draw_status_bar(self, statuses):
        icons_to_draw = [
            "DOCKER_OK" if statuses["status_docker"] else "DOCKER_FAIL",
            "STORAGE_OK" if statuses["status_root_disk"] else "STORAGE_FAIL",
            "NVME_OK" if statuses["status_storage_disk"] else "NVME_FAIL",
            "WIFI_OK" if statuses["status_wifi"] else "WIFI_FAIL",
            "VOLTAGE_OK" if statuses["status_voltage"] else "VOLTAGE_FAIL",
        ]
        positions = [0, 30, 60, 90, 120]
        for i, icon_name in enumerate(icons_to_draw):
            self.image.paste(self.icons[icon_name], (positions[i], 0))