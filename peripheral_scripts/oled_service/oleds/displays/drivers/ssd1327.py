#!/usr/bin/env python3
import os
from PIL import Image
from luma.core.interface.serial import spi
from luma.oled.device import ssd1327

from .base import BaseDisplayDriver 

class SSD1327_Driver(BaseDisplayDriver):
    def __init__(self):
        port = int(os.getenv("OLED_SPI_PORT", "0"))          # 0
        device = int(os.getenv("OLED_SPI_DEVICE", "0"))      # CE0 = 0, CE1 = 1
        dc = int(os.getenv("OLED_DC_PIN", "25"))             # GPIO25 (Pin 22)
        rst = int(os.getenv("OLED_RST_PIN", "27"))           # GPIO27 (Pin 13)
        speed = int(os.getenv("OLED_SPI_SPEED", "2000000"))  # 2 MHz

        width = int(os.getenv("OLED_WIDTH", "128"))
        height = int(os.getenv("OLED_HEIGHT", "128"))
        rotate = int(os.getenv("OLED_ROTATE", "0"))  # 0/1/2/3

        self.image_mode = os.getenv("OLED_IMAGE_MODE", "RGB")

        serial = spi(port=port, device=device, gpio_DC=dc, gpio_RST=rst, bus_speed_hz=speed)
        self._dev = ssd1327(serial_interface=serial, width=width, height=height, rotate=rotate)

        self._width = width
        self._height = height

        self.clear()

    def clear(self):
        if self.image_mode == "RGB":
            img = Image.new("RGB", (self._width, self._height), "black")
        else:
            img = Image.new("1", (self._width, self._height))
        self._dev.display(img)

    def show(self, image):
        img = image
        if img.mode not in ("1", "RGB"):
            img = img.convert(self.image_mode)
        elif self.image_mode != img.mode:
            img = img.convert(self.image_mode)

        self._dev.display(img)

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height
