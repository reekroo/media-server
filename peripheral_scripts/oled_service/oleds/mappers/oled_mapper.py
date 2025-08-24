#!/usr/bin/env python3
from configs.oled_configs import DOCKER_STATUS_MAP

def map_docker_status(raw_status: str) -> str:
    if not raw_status:
        return "N/A"
    return DOCKER_STATUS_MAP.get(raw_status, raw_status[:4])
