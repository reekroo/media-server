#!/usr/bin/env python3

import psutil
import time

class DiskProvider:
    def __init__(self, path='/'):
        self.path = path
        self.last_check_time = time.time()
        self.last_read_bytes = 0
        self.last_write_bytes = 0
        
    def get_usage(self):
        return psutil.disk_usage(self.path).percent

    def get_io(self):
        current_time = time.time()
        time_delta = current_time - self.last_check_time
        
        disk_io = psutil.disk_io_counters()
        read_bytes = disk_io.read_bytes
        write_bytes = disk_io.write_bytes
        
        if time_delta > 0:
            read_speed = (read_bytes - self.last_read_bytes) / time_delta
            write_speed = (write_bytes - self.last_write_bytes) / time_delta
        else:
            read_speed, write_speed = 0, 0
            
        self.last_check_time = current_time
        self.last_read_bytes = read_bytes
        self.last_write_bytes = write_bytes
        
        def format_speed(speed_bytes):
            if speed_bytes > 1024 * 1024:
                return f"{speed_bytes / (1024*1024):.1f}M"
            return f"{speed_bytes / 1024:.0f}K"
            
        return {
            "read": format_speed(read_speed),
            "write": format_speed(write_speed)
        }