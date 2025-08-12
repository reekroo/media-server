#!/usr/bin/env python3

from board import SCL, SDA
import busio
from PIL import Image, ImageDraw, ImageFont
import adafruit_ssd1306
import sys

sys.path.append('/home/reekroo/scripts')
from oleds.configs.oled_icons import ICON_DATA
from .screens import performance_screen, storage_screen, health_screen

class DisplayManager:
    def __init__(self):
        i2c = busio.I2C(SCL, SDA)
        self.disp = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
        self.width, self.height = self.disp.width, self.disp.height
        self.image = Image.new("1", (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)
        try:
            self.font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
        except IOError:
            self.font = ImageFont.load_default()
        
        self.icons = {name: Image.frombytes('1', (8, 8), bytes(data)) for name, data in ICON_DATA.items()}

    def clear(self):
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

    def draw_status_bar(self, statuses):
        icons_to_draw = [
            "DOCKER_OK" if statuses["status_docker"] else "DOCKER_FAIL",
            "STORAGE_OK" if statuses["status_root_disk"] else "STORAGE_FAIL",
            "STORAGE_OK" if statuses["status_storage_disk"] else "STORAGE_FAIL",
            "WIFI_OK" if statuses["status_wifi"] else "WIFI_FAIL",
            "VOLTAGE_OK" if statuses["status_voltage"] else "VOLTAGE_FAIL",
        ]

        positions = [0, 30, 60, 90, 120]

        for i, icon_name in enumerate(icons_to_draw):
            self.image.paste(self.icons[icon_name], (positions[i], 0))

    def draw_page_performance(self, stats):
        performance_screen.draw(self, stats)

    def draw_page_storage(self, stats):
        storage_screen.draw(self, stats)

    def draw_page_health(self, stats):
        health_screen.draw(self, stats)

    def show(self):
        self.disp.image(self.image)
        self.disp.show()