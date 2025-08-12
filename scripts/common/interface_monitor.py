#!/usr/bin/env python3

import subprocess

class InterfaceMonitor:
    def __init__(self, interface_name):
        self.interface_name = interface_name

    def is_up(self):
        try:
            result = subprocess.run(
                ['ip', 'addr', 'show', self.interface_name],
                capture_output=True, text=True, check=True
            )
            return 'state UP' in result.stdout
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
