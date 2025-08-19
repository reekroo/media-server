# ~/metrics_exporter/src/providers/disk_provider.py

import psutil
import time

class DiskProvider:
    def __init__(self, path='/'):
        self.path = path
        self.last_check_time = 0
        self.last_read_bytes = 0
        self.last_write_bytes = 0
        self.get_io()
        
    def get_usage(self):
        try:
            usage = psutil.disk_usage(self.path)
            return {"used": usage.used, "total": usage.total, "percent": usage.percent}
        except FileNotFoundError:
            return {"used": 0, "total": 0, "percent": 0}

    def get_io(self):
        current_time = time.time()
        disk_io = psutil.disk_io_counters()
        read_bytes = disk_io.read_bytes
        write_bytes = disk_io.write_bytes

        time_delta = current_time - self.last_check_time
        
        read_speed, write_speed = 0, 0
        if time_delta > 0 and self.last_check_time > 0:
            read_speed = (read_bytes - self.last_read_bytes) / time_delta
            write_speed = (write_bytes - self.last_write_bytes) / time_delta
            
        self.last_check_time = current_time
        self.last_read_bytes = read_bytes
        self.last_write_bytes = write_bytes
        
        def format_speed(speed_bytes):
            if speed_bytes > (1024 * 1024):
                return f"{speed_bytes / (1024*1024):.1f} MB/s"
            return f"{speed_bytes / 1024:.0f} KB/s"
            
        return {
            "read": format_speed(read_speed),
            "write": format_speed(write_speed)
        }