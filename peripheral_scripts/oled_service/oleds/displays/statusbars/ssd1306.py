#!/usr/bin/env python3
from typing import Dict

from .base import StatusBarBase

class StatusBarSSD1306(StatusBarBase):
    def draw(self, dm, statuses: Dict):
        icons = [
            "DOCKER_OK" if statuses.get("status_docker") else "DOCKER_FAIL",
            "STORAGE_OK" if statuses.get("status_root_disk") else "STORAGE_FAIL",
            "NVME_OK" if statuses.get("status_storage_disk") else "NVME_FAIL",
            "WIFI_OK" if statuses.get("status_wifi") else "WIFI_FAIL",
            "VOLTAGE_OK" if statuses.get("status_voltage") else "VOLTAGE_FAIL",
        ]

        positions = [0, 30, 60, 90, 120]
        
        for i, name in enumerate(icons):
            icon = dm._get_icon(name)
            if icon:
                dm.image.paste(icon, (positions[i], 0))