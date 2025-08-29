import adafruit_ssd1306
from board import SCL, SDA
import busio

from .base import BaseDisplayDriver

class SSD1306_Driver(BaseDisplayDriver):
    def __init__(self, width=128, height=64):
        i2c = busio.I2C(SCL, SDA)
        self.disp = adafruit_ssd1306.SSD1306_I2C(width, height, i2c)

    def clear(self):
        self.disp.fill(0)
        self.disp.show()

    def show(self, image):
        self.disp.image(image)
        self.disp.show()

    @property
    def width(self) -> int:
        return self.disp.width

    @property
    def height(self) -> int:
        return self.disp.height