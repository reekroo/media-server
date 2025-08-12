#!/usr/bin/env python3

import psutil
import time
import datetime

class SystemProvider:
    
    def get_cpu_usage(self):
        return psutil.cpu_percent()
    
    def get_mem_usage(self):
        return psutil.virtual_memory().percent
    
    def get_swap_usage(self):
        return psutil.swap_memory().percent
        
    def get_cpu_temp(self):
        try:
            temps = psutil.sensors_temperatures()
            if 'cpu_thermal' in temps:
                return temps['cpu_thermal'][0].current
        except (KeyError, IndexError):
            pass
        return 0
        
    def get_uptime(self):
        uptime_seconds = time.time() - psutil.boot_time()
        uptime_delta = datetime.timedelta(seconds=uptime_seconds)
        days = uptime_delta.days
        hours, rem = divmod(uptime_delta.seconds, 3600)
        minutes, _ = divmod(rem, 60)
        return f"{days}d {hours:02}:{minutes:02}" if days > 0 else f"{hours:02}:{minutes:02}"