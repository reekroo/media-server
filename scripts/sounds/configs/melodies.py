#!/usr/bin/env python3

WIFI_TOGGLE = [('C5', 0.05), ('G5', 0.05)]
REBOOT_SYSTEM = [('A5', 0.1), ('A5', 0.1), ('A5', 0.1)]

SUCCESS = [("E6", 0.1), (None, 0.05), ("E6", 0.1)]
FAILURE = [("C4", 0.2)]

BOOT = [("C5", 0.1), (None, 0.05), ("C5", 0.1)]
SHUTDOWN = [("G4", 0.1), (None, 0.05), ("G4", 0.1)]
REBOOT = [("A5", 0.08), (None, 0.05), ("A5", 0.08), (None, 0.05), ("A5", 0.08)]

ALERT_LEVEL_1 = [('E6', 0.15), (None, 0.5)]
ALERT_LEVEL_2 = [('E6', 0.15), (None, 0.2)]
ALERT_LEVEL_3 = [('E6', 0.1), (None, 0.05), ('E6', 0.1), (None, 0.3)]
ALERT_LEVEL_4 = [('E6', 0.2), ('A5', 0.2)]
ALERT_LEVEL_5 = [('E6', 0.15), ('A5', 0.15)]
