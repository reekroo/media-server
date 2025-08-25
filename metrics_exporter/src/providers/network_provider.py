import netifaces as ni
import psutil
import time

class NetworkProvider:
    def __init__(self, lan_if='eth0', wlan_if='wlan0'):
        self.lan_if = lan_if
        self.wlan_if = wlan_if
        self.last_check_time = 0.0
        self.last_bytes_sent = 0
        self.last_bytes_recv = 0
        self._prime_counters()

    def _prime_counters(self):
        io = psutil.net_io_counters()
        self.last_check_time = time.time()
        self.last_bytes_sent = io.bytes_sent
        self.last_bytes_recv = io.bytes_recv

    def get_ip_address(self):
        for interface in (self.lan_if, self.wlan_if):
            try:
                return ni.ifaddresses(interface)[ni.AF_INET][0]['addr']
            except (ValueError, KeyError, IndexError):
                continue
        return "N/A"

    def get_throughput(self):
        now = time.time()
        io = psutil.net_io_counters()
        sent = io.bytes_sent
        recv = io.bytes_recv

        dt = now - self.last_check_time if self.last_check_time else 0.0
        up_bps = 0.0
        down_bps = 0.0
        if dt > 0:
            up_bps = max(0.0, (sent - self.last_bytes_sent) / dt)
            down_bps = max(0.0, (recv - self.last_bytes_recv) / dt)

        self.last_check_time = now
        self.last_bytes_sent = sent
        self.last_bytes_recv = recv

        def human(speed_bytes: float) -> str:
            if speed_bytes >= 1024 * 1024:
                return f"{speed_bytes / (1024 * 1024):.1f} MB/s"
            return f"{speed_bytes / 1024:.0f} KB/s"

        return {
            "upload_bytes_per_sec": up_bps,
            "download_bytes_per_sec": down_bps,
            "upload_human_per_sec": human(up_bps),
            "download_human_per_sec": human(down_bps),
        }
