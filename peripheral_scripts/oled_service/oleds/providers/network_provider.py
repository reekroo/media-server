#!/usr/bin/env python3
import time
import socket
import subprocess
from shutil import which

import netifaces as ni
import psutil

from utils.wifi_controller import WifiController

class NetworkProvider:
    def __init__(self, lan_if: str = "eth0", wlan_if: str = "wlan0"):
        self.lan_if = lan_if
        self.wlan_if = wlan_if
        self._wifi_controller = WifiController()

        self.last_check_time = time.time()
        io = psutil.net_io_counters()
        self.last_bytes_sent = io.bytes_sent
        self.last_bytes_recv = io.bytes_recv

    def _ip_for_if(self, ifname: str) -> str | None:
        try:
            addrs = ni.ifaddresses(ifname)
            ipv4 = addrs.get(ni.AF_INET, [])
            return ipv4[0]["addr"] if ipv4 else None
        except (ValueError, KeyError, IndexError):
            return None

    def get_ip_address(self) -> str:
        """
        Совместимо со старым кодом: сначала LAN, потом Wi-Fi.
        """
        for ifname in (self.lan_if, self.wlan_if):
            ip = self._ip_for_if(ifname)
            if ip:
                return ip
        return "N/A"

    def get_lan_ip(self) -> str | None:
        return self._ip_for_if(self.lan_if)

    def get_wlan_ip(self) -> str | None:
        return self._ip_for_if(self.wlan_if)

    def _iface_is_up(self, ifname: str) -> bool:
        st = psutil.net_if_stats().get(ifname)
        return bool(st and st.isup)

    def is_lan_connected(self) -> bool:
        """
        Считаем LAN включённым, если интерфейс up И есть IPv4.
        """
        return self._iface_is_up(self.lan_if) and bool(self.get_lan_ip())

    def is_wifi_connected(self) -> bool:
        """
        Включён + up + есть IPv4.
        """
        return (not self._wifi_controller.is_blocked()) and self._iface_is_up(self.wlan_if) and bool(self.get_wlan_ip())

    def is_wifi_enabled(self) -> bool:
        """
        Оставляем старый метод для обратной совместимости: просто «не заблокирован».
        """
        return not self._wifi_controller.is_blocked()

    def is_bluetooth_enabled(self) -> bool | None:
        """
        True/False если смогли определить; None — если утилит нет.
        Проверяем по bluetoothctl/hciconfig/rfkill.
        """
        # bluetoothctl show -> "Powered: yes"
        if which("bluetoothctl"):
            try:
                out = subprocess.run(
                    ["bluetoothctl", "show"],
                    check=False, capture_output=True, text=True, timeout=0.5
                ).stdout.lower()
                if "powered: yes" in out:
                    return True
                if "powered: no" in out:
                    return False
            except Exception:
                pass

        # hciconfig -> "UP RUNNING"
        if which("hciconfig"):
            try:
                out = subprocess.run(
                    ["hciconfig"],
                    check=False, capture_output=True, text=True, timeout=0.5
                ).stdout.lower()
                if "up" in out:
                    return True
                if "down" in out:
                    return False
            except Exception:
                pass

        # rfkill list bluetooth -> Soft blocked: yes/no
        if which("rfkill"):
            try:
                out = subprocess.run(
                    ["rfkill", "list", "bluetooth"],
                    check=False, capture_output=True, text=True, timeout=0.5
                ).stdout.lower()
                if "soft blocked: yes" in out or "hard blocked: yes" in out:
                    return False
                if "soft blocked: no" in out:
                    return True
            except Exception:
                pass

        return None  # не смогли определить

    def get_throughput(self) -> dict:
        current_time = time.time()
        time_delta = max(1e-6, current_time - self.last_check_time)

        net_io = psutil.net_io_counters()
        bytes_sent = net_io.bytes_sent
        bytes_recv = net_io.bytes_recv

        upload_speed = (bytes_sent - self.last_bytes_sent) / time_delta
        download_speed = (bytes_recv - self.last_bytes_recv) / time_delta

        self.last_check_time = current_time
        self.last_bytes_sent = bytes_sent
        self.last_bytes_recv = bytes_recv

        def fmt(speed):
            if speed >= 1024 * 1024:
                return f"{speed / (1024*1024):.1f}M/s"
            return f"{speed / 1024:.0f}K/s"

        return {"upload": fmt(upload_speed), "download": fmt(download_speed)}
