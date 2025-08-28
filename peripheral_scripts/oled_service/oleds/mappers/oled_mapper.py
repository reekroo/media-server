#!/usr/bin/env python3
from oleds.models.statuses import DOCKER_STATUS_MAP

def map_docker_status(raw_status: str) -> str:
    if not raw_status:
        return "N/A"
    return DOCKER_STATUS_MAP.get(raw_status, raw_status[:4])
