
import psutil
import time
import datetime

class SystemProvider:
    
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
            temps = psutil.sensors_temperatures()
            if 'cpu_thermal' in temps:
                return temps['cpu_thermal'][0].current
        except (AttributeError, KeyError, IndexError):
            pass
        return 0.0
        
    def get_cpu_frequency(self):
        try:
            freq = psutil.cpu_freq()
            return freq.current if freq else 0
        except Exception:
            return 0

    def get_uptime(self):
        try:
            uptime_seconds = time.time() - psutil.boot_time()
            uptime_delta = datetime.timedelta(seconds=uptime_seconds)
            days = uptime_delta.days
            hours, rem = divmod(uptime_delta.seconds, 3600)
            minutes, _ = divmod(rem, 60)
            if days > 0:
                return f"{days}d {hours:02}h{minutes:02}m"
            return f"{hours:02}h{minutes:02}m"
        except Exception:
            return "N/A"