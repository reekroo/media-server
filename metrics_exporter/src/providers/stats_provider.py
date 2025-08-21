from providers.system_provider import SystemProvider
from providers.network_provider import NetworkProvider
from providers.disk_provider import DiskProvider
from providers.docker_provider import DockerProvider
from providers.hardware_provider import HardwareProvider

class StatsProvider:
    def __init__(self):
        self.system = SystemProvider()
        self.network = NetworkProvider()
        self.root_disk = DiskProvider(path='/')
        self.storage_disk = DiskProvider(path='/mnt/storage/')
        self.docker = DockerProvider()
        self.hardware = HardwareProvider()

    def get_all_stats(self):
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
            "docker_stats": self.docker.get_stats(),
            "nvme_health": self.hardware.get_nvme_health(),
            "core_voltage": self.hardware.get_core_voltage(),
            "network_throughput": self.network.get_throughput(),
            "disk_io": self.storage_disk.get_io(),
            "throttling": self.hardware.get_throttling_status()
        }
        return stats