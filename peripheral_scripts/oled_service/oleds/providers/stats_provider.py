#!/usr/bin/env python3

from .system_provider import SystemProvider
from .network_provider import NetworkProvider
from .disk_provider import DiskProvider
from .docker_provider import DockerProvider
from .hardware_provider import HardwareProvider

class StatsProvider:
    def __init__(self):
        self.system = SystemProvider()
        self.network = NetworkProvider()
        self.root_disk = DiskProvider(path='/')
        self.storage_disk = DiskProvider(path='/mnt/storage/')
        self.docker = DockerProvider()
        self.hardware = HardwareProvider()

    def get_all_stats(self):
        disk = self.root_disk.get_usage()
        docker_stats = self.docker.get_stats()
        nvme_health = self.hardware.get_nvme_health()
        throttling_status = self.hardware.get_throttling_status()

        stats = {
            "ip": self.network.get_ip_address(),
            "cpu": self.system.get_cpu_usage(),
            "cpu_freq": self.system.get_cpu_frequency(),
            "mem": self.system.get_mem_usage(),
            "swap": self.system.get_swap_usage(),
            "temp": self.system.get_cpu_temp(),
            "uptime": self.system.get_uptime(),
            "root_disk_usage": self.root_disk.get_usage(),
            "storage_disk_usage": self.storage_disk.get_usage(),
            "docker_restarts": docker_stats["restarts"],
            "docker_status": docker_stats["status"],
            "nvme_temp": nvme_health["temperature"],
            "core_voltage": self.hardware.get_core_voltage(),
            "network_throughput": self.network.get_throughput(),

            "disk_io": self.storage_disk.get_io(),
            "throttling": throttling_status,

            "status_docker": docker_stats["is_running"],
            "status_root_disk": disk['percent'] < 90,
            "status_storage_disk": nvme_health["critical_warning"] == 0,
            "status_wifi": self.network.is_wifi_enabled(),
            "status_voltage": self.hardware.get_core_voltage() > 4.75,
            
            "lan_ip": self.network.get_lan_ip(),
            "wifi_ip": self.network.get_wlan_ip(),
            "status_lan": self.network.is_lan_connected(),
            "status_wifi_connected": self.network.is_wifi_connected(),
            "status_bluetooth": self.network.is_bluetooth_enabled(),
        }
        return stats