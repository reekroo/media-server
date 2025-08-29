#!/usr/bin/env python3
from typing import Dict, Tuple

WHITE_1BIT = 255
WHITE_RGB: Tuple[int, int, int] = (255, 255, 255)

class StatusBarBase:
    def __init__(self, icon_size: int, image_mode: str):
        self.icon_size = icon_size
        self.image_mode = image_mode

    def color(self):
        return WHITE_RGB if self.image_mode != "1" else WHITE_1BIT

    def draw(self, dm, statuses: Dict):
        raise NotImplementedError