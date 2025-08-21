#!/usr/-bin/env python3

DOCKER_STATUS_MAP = {
    "running": "OK",
    "exited": "STOP",
    "restarting": "RST",
    "paused": "PAUSE"
}