import psutil
import time

class DiskProvider:
    def __init__(self, path='/'):
        self.path = path
        self.last_check_time = 0.0
        self.last_read_bytes = 0
        self.last_write_bytes = 0
        self._prime_counters()

    def _prime_counters(self):
        _ = psutil.disk_io_counters()
        self.last_check_time = time.time()
        self.last_read_bytes = _.read_bytes
        self.last_write_bytes = _.write_bytes

    def get_usage(self):
        try:
            usage = psutil.disk_usage(self.path)
            return {"used": usage.used, "total": usage.total, "percent": usage.percent}
        except FileNotFoundError:
            return {"used": 0, "total": 0, "percent": 0}

    def get_io(self):
        now = time.time()
        io = psutil.disk_io_counters()
        read_bytes = io.read_bytes
        write_bytes = io.write_bytes

        dt = now - self.last_check_time if self.last_check_time else 0.0

        read_bps = 0.0
        write_bps = 0.0
        if dt > 0:
            read_bps = max(0.0, (read_bytes - self.last_read_bytes) / dt)
            write_bps = max(0.0, (write_bytes - self.last_write_bytes) / dt)

        self.last_check_time = now
        self.last_read_bytes = read_bytes
        self.last_write_bytes = write_bytes

        def human(speed_bytes: float) -> str:
            if speed_bytes >= 1024 * 1024:
                return f"{speed_bytes / (1024 * 1024):.1f} MB/s"
            return f"{speed_bytes / 1024:.0f} KB/s"

        return {
            "read_bytes_per_sec": read_bps,
            "write_bytes_per_sec": write_bps,
            "read_human_per_sec": human(read_bps),
            "write_human_per_sec": human(write_bps),
        }
