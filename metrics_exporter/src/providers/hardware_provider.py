
import subprocess
import json

class HardwareProvider:

    def get_core_voltage(self):
        try:
            result = subprocess.run(['vcgencmd', 'measure_volts', 'core'], capture_output=True, text=True, check=True)
            return float(result.stdout.split('=')[1][:-2])
        except (subprocess.CalledProcessError, FileNotFoundError, IndexError, ValueError):
            return 0.0

    def get_nvme_health(self):
        health_stats = {
            "critical_warning": 1,
            "temperature": 0
        }
        try:
            result = subprocess.run(['nvme', 'smart-log', '/dev/nvme0', '-o', 'json'], capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
            health_stats["critical_warning"] = data.get("critical_warning", 1)
            
            temperature_celsius = data.get("temperature", 273) - 273
            health_stats["temperature"] = temperature_celsius
            
        except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
            pass
        return health_stats

    def get_throttling_status(self):
        status_map = {
            0: "Under-voltage detected",
            1: "Arm frequency capped",
            2: "Currently throttled",
            16: "Under-voltage has occurred",
            17: "Arm frequency capping has occurred",
            18: "Throttling has occurred",
        }
        try:
            result = subprocess.run(['vcgencmd', 'get_throttled'], capture_output=True, text=True, check=True)
            hex_code = int(result.stdout.strip().split('=')[1], 16)
            
            if hex_code == 0:
                return "Not throttled"
            
            active_statuses = []
            for bit, message in status_map.items():
                if (hex_code >> bit) & 1:
                    active_statuses.append(message)
            return ", ".join(active_statuses) if active_statuses else "Throttled (Unknown)"
        except (subprocess.CalledProcessError, FileNotFoundError, IndexError, ValueError):
            return "N/A"