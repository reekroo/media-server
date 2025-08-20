import netifaces as ni
import psutil
import time

class NetworkProvider:
    def __init__(self, lan_if='eth0', wlan_if='wlan0'):
        self.lan_if = lan_if
        self.wlan_if = wlan_if
        self.last_check_time = 0
        self.last_bytes_sent = 0
        self.last_bytes_recv = 0
        self.get_throughput()

    def get_ip_address(self):
        for interface in [self.lan_if, self.wlan_if]:
            try:
                return ni.ifaddresses(interface)[ni.AF_INET][0]['addr']
            except (ValueError, KeyError, IndexError):
                continue
        return "N/A"

    def get_throughput(self):
        current_time = time.time()
        net_io = psutil.net_io_counters()
        bytes_sent = net_io.bytes_sent
        bytes_recv = net_io.bytes_recv

        time_delta = current_time - self.last_check_time
        
        upload_speed, download_speed = 0, 0
        if time_delta > 0 and self.last_check_time > 0:
            upload_speed = (bytes_sent - self.last_bytes_sent) / time_delta
            download_speed = (bytes_recv - self.last_bytes_recv) / time_delta
        
        self.last_check_time = current_time
        self.last_bytes_sent = bytes_sent
        self.last_bytes_recv = bytes_recv

        def format_speed(speed_bytes):
            if speed_bytes > (1024 * 1024):
                return f"{speed_bytes / (1024*1024):.1f} MB/s"
            return f"{speed_bytes / 1024:.0f} KB/s"

        return {
            "upload": format_speed(upload_speed),
            "download": format_speed(download_speed)
        }