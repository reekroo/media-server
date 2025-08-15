BOOT = [('C4', 0.1), ('E4', 0.1), ('G4', 0.1), ('C5', 0.2)]
SHUTDOWN = [('C5', 0.2), ('G4', 0.1), ('E4', 0.1), ('C4', 0.1)]

WIFI_TOGGLE = [('C5', 0.05), ('G5', 0.05)]
REBOOT_SYSTEM = [('A5', 0.1), ('A5', 0.1), ('A5', 0.1)]

ALERT_LEVEL_1 = [('A5', 0.15), (None, 0.5)]
ALERT_LEVEL_2 = [('A5', 0.15), (None, 0.2)]
ALERT_LEVEL_3 = [('A5', 0.1), (None, 0.05), ('A5', 0.1), (None, 0.3)]
ALERT_LEVEL_4 = [('A5', 0.2), ('G5', 0.2)]
ALERT_LEVEL_5 = [('A5', 0.15), ('G5', 0.15)]

ALL_MELODIES = {
    "BOOT": BOOT,
    "SHUTDOWN": SHUTDOWN,
    "WIFI_TOGGLE": WIFI_TOGGLE,
    "REBOOT_SYSTEM": REBOOT_SYSTEM,
    "ALERT_LEVEL_1": ALERT_LEVEL_1,
    "ALERT_LEVEL_2": ALERT_LEVEL_2,
    "ALERT_LEVEL_3": ALERT_LEVEL_3,
    "ALERT_LEVEL_4": ALERT_LEVEL_4,
    "ALERT_LEVEL_5": ALERT_LEVEL_5,
}
