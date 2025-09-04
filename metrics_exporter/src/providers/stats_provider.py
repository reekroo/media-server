class StatsProvider:
    def __init__(self, system_p, network_p, root_disk_p, storage_disk_p, docker_p, hardware_p):
        self.system = system_p
        self.network = network_p
        self.root_disk = root_disk_p
        self.storage_disk = storage_disk_p
        self.docker = docker_p
        self.hardware = hardware_p

    def get_all_stats(self) -> dict:
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