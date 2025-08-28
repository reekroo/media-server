#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFont
from configs.oled_icons import ICON_DATA
from configs.configs import FONT_PATH, FONT_SIZE

class DisplayManager:
    def __init__(self, driver):
        self.driver = driver
        self.width = self.driver.width
        self.height = self.driver.height

        self.image_mode = getattr(self.driver, "image_mode", "1")

        self.image = Image.new(self.image_mode, (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)
        try:
            self.font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
        except Exception:
            self.font = ImageFont.load_default()

        self.icons = {}
        for name, data in ICON_DATA.items():
            icon = Image.frombytes('1', (8, 8), bytes(data))
            if self.image_mode != '1':
                icon = icon.convert(self.image_mode)
            self.icons[name] = icon

    def clear(self):
        if self.image_mode == "RGB":
            self.draw.rectangle((0, 0, self.width, self.height), outline=None, fill=(0, 0, 0))
        else:
            self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

    def show(self):
        self.driver.show(self.image)

    def _get_icon(self, name: str):
        img = self.icons.get(name)
        if img is None and name in ICON_DATA:
            icon = Image.frombytes('1', (8, 8), bytes(ICON_DATA[name]))
            if self.image_mode != '1':
                icon = icon.convert(self.image_mode)
            self.icons[name] = icon
            img = self.icons[name]
        return img

    def draw_status_bar(self, statuses: dict):
        icons_to_draw = [
            "DOCKER_OK" if statuses.get("status_docker") else "DOCKER_FAIL",
            "STORAGE_OK" if statuses.get("status_root_disk") else "STORAGE_FAIL",
            "NVME_OK" if statuses.get("status_storage_disk") else "NVME_FAIL",
            "WIFI_OK" if statuses.get("status_wifi") else "WIFI_FAIL",
            "VOLTAGE_OK" if statuses.get("status_voltage") else "VOLTAGE_FAIL",
        ]
        positions = [0, 30, 60, 90, 120]
        for i, icon_name in enumerate(icons_to_draw):
            icon = self._get_icon(icon_name)
            if icon:
                self.image.paste(icon, (positions[i], 0))
