# src/melodies.py

NOTES = {
    'C4': 261.63, 'G4': 392.00,
    'C5': 523.25, 'G5': 783.99, 'A5': 880.00,
    'E6': 1318.51,
}

ALERT_LEVEL_1 = [(440, 0.15), (None, 0.5)]
ALERT_LEVEL_2 = [(550, 0.15), (None, 0.2)]
ALERT_LEVEL_3 = [(660, 0.1), (None, 0.05), (660, 0.1), (None, 0.3)]
ALERT_LEVEL_4 = [(770, 0.2), (880, 0.2)]
ALERT_LEVEL_5 = [(900, 0.15), (1100, 0.15)]

MELODY_MAP = {
    'ALERT_LEVEL_1': ALERT_LEVEL_1,
    'ALERT_LEVEL_2': ALERT_LEVEL_2,
    'ALERT_LEVEL_3': ALERT_LEVEL_3,
    'ALERT_LEVEL_4': ALERT_LEVEL_4,
    'ALERT_LEVEL_5': ALERT_LEVEL_5,
}