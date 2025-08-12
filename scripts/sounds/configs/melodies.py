#!/usr/bin/env python3

WIFI_ON = [("C5", 0.1), ("G5", 0.1)]
WIFI_OFF = [("G5", 0.1), ("C5", 0.1)]

SUCCESS = [("E6", 0.1), (None, 0.05), ("E6", 0.1)]
FAILURE = [("C4", 0.2)]

BOOT = [("C5", 0.1), (None, 0.05), ("C5", 0.1)]
SHUTDOWN = [("G4", 0.1), (None, 0.05), ("G4", 0.1)]
REBOOT = [("A5", 0.08), (None, 0.05), ("A5", 0.08), (None, 0.05), ("A5", 0.08)]