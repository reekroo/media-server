#!/usr/bin/env python3

import sys
sys.path.append('/home/reekroo/peripheral_scripts')

from oleds.configs.oled_configs import DOCKER_STATUS_MAP

def map_docker_status(raw_status):
    return DOCKER_STATUS_MAP.get(raw_status, raw_status[:4])