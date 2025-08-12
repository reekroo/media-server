#!/usr/bin/env python3

import subprocess
import json

class HardwareProvider:

    def get_core_voltage(self):
        try:
            result = subprocess.run(['vcgencmd', 'measure_volts', 'core'], capture_output=True, text=True)
            return float(result.stdout.split('=')[1][:-2])
        except (FileNotFoundError, IndexError, ValueError):
            return 0.0

    def get_psu_voltage(self):
        try:
            result = subprocess.run(['vcgencmd', 'measure_volts', 'usb'], capture_output=True, text=True)
            return float(result.stdout.split('=')[1][:-2])
        except (FileNotFoundError, IndexError, ValueError):
            return 0.0

    def get_nvme_health(self):
        health_stats = {
            "critical_warning": 1,
            "temperature": 0
        }
        try:
            result = subprocess.run(['nvme', 'smart-log', '/dev/nvme0', '-o', 'json'], capture_output=True, text=True)
            data = json.loads(result.stdout)
            health_stats["critical_warning"] = data.get("critical_warning", 1)
            health_stats["temperature"] = data.get("temperature", 0)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        return health_stats

    def get_nvme_set_power_state(self):
        try:
            cmd = ['sudo', 'nvme', 'get-feature', '/dev/nvme0', '-f', '0x02', '-H']
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.stdout.strip()[-1]
        except (FileNotFoundError, IndexError):
            return "?"

    def get_nvme_current_power_state(self):
        try:
            cmd = ['sudo', 'nvme', 'smart-log', '/dev/nvme0', '-o', 'json']
            result = subprocess.run(cmd, capture_output=True, text=True)
            data = json.loads(result.stdout)
            
            state_index = data.get('active_power_state')
            if state_index is not None:
                return str(state_index)
            
            state_index = data.get('ps')
            if state_index is not None:
                return str(state_index)

        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            pass
        return "?"

    def get_throttling_status(self):
        status_map = {
            0: "Under-voltage",
            1: "Arm frequency capped",
            2: "Currently throttled",
            16: "Under-voltage has occurred",
            17: "Arm frequency capping has occurred",
            18: "Throttling has occurred",
        }
        try:
            result = subprocess.run(['vcgencmd', 'get_throttled'], capture_output=True, text=True)
            hex_code = int(result.stdout.strip().split('=')[1], 16)
            
            if hex_code == 0:
                return "NO"
            
            for bit, message in status_map.items():
                if (hex_code >> bit) & 1:
                    return f"YES ({message.split(' ')[0]})" # Возвращаем короткую причину
            return "YES (Unknown)"
        except (FileNotFoundError, IndexError, ValueError):
            return "N/A"