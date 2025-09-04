import psutil
import time
import logging

class SystemProvider:
    def __init__(self, logger: logging.Logger):
        self.log = logger
    
    def get_cpu_usage(self):
        return psutil.cpu_percent()
        
    def get_mem_usage(self):
        mem = psutil.virtual_memory()
        return {"used": mem.used, "total": mem.total, "percent": mem.percent}

    def get_swap_usage(self):
        swap = psutil.swap_memory()
        return {"used": swap.used, "total": swap.total, "percent": swap.percent}
        
    def get_cpu_temp(self):
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                temp = int(f.read().strip()) / 1000.0
                return temp
        except (FileNotFoundError, IndexError, ValueError):
            self.log.warning("Could not read CPU temperature from thermal_zone0.")
            return 0.0
        
    def get_cpu_frequency(self):
        try:
            freq = psutil.cpu_freq()
            return freq.current if freq else 0
        except Exception:
            return 0

    def get_uptime(self):
        return time.time() - psutil.boot_time()