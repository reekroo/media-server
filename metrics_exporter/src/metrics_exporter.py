import logging
from prometheus_client import Gauge

class PrometheusExporter:
    def __init__(self, logger: logging.Logger):
        self.log = logger
        self._metrics = {
            'cpu_usage': Gauge('rpi_cpu_usage_percent', 'Current CPU usage percentage'),
            'cpu_freq': Gauge('rpi_cpu_frequency_mhz', 'Current CPU frequency in MHz'),
            'cpu_temp': Gauge('rpi_cpu_temperature_celsius', 'CPU temperature in Celsius'),
            'ram_usage': Gauge('rpi_ram_usage_percent', 'RAM usage percentage'),
            'swap_usage': Gauge('rpi_swap_usage_percent', 'Swap usage percentage'),
            'core_voltage': Gauge('rpi_core_voltage_volts', 'Core voltage of the RPi'),
            'uptime': Gauge('rpi_uptime_seconds', 'System uptime in seconds'),
            'disk_usage': Gauge('rpi_disk_usage_percent', 'Disk usage percentage', ['path']),
            'disk_read': Gauge('rpi_disk_read_bytes_per_second', 'Disk read speed in B/s', ['path']),
            'disk_write': Gauge('rpi_disk_write_bytes_per_second', 'Disk write speed in B/s', ['path']),
            'net_upload': Gauge('rpi_network_upload_bytes_per_second', 'Network upload speed in B/s'),
            'net_download': Gauge('rpi_network_download_bytes_per_second', 'Network download speed in B/s'),
            'docker_total': Gauge('rpi_docker_containers_total', 'Total number of Docker containers'),
            'docker_running': Gauge('rpi_docker_containers_running', 'Number of running Docker containers'),
            'nvme_temp': Gauge('rpi_nvme_temperature_celsius', 'NVMe disk temperature in Celsius')
        }

    def update(self, all_stats: dict):
        try:
            if 'cpu' in all_stats: self._metrics['cpu_usage'].set(all_stats['cpu'])
            if 'cpu_freq' in all_stats: self._metrics['cpu_freq'].set(all_stats['cpu_freq'])
            if 'temp' in all_stats: self._metrics['cpu_temp'].set(all_stats['temp'])
            if 'core_voltage' in all_stats: self._metrics['core_voltage'].set(all_stats['core_voltage'])
            if 'uptime' in all_stats: self._metrics['uptime'].set(all_stats['uptime'])

            if all_stats.get('mem'):
                self._metrics['ram_usage'].set(all_stats['mem'].get('percent', 0))
            if all_stats.get('swap'):
                self._metrics['swap_usage'].set(all_stats['swap'].get('percent', 0))
            if all_stats.get('nvme_health'):
                self._metrics['nvme_temp'].set(all_stats['nvme_health'].get('temperature', 0))

            if all_stats.get('root_disk_usage'):
                self._metrics['disk_usage'].labels(path='/').set(all_stats['root_disk_usage'].get('percent', 0))
            if all_stats.get('storage_disk_usage'):
                self._metrics['disk_usage'].labels(path='/mnt/storage').set(all_stats['storage_disk_usage'].get('percent', 0))

            if all_stats.get('disk_io'):
                self._metrics['disk_read'].labels(path='/mnt/storage').set(all_stats['disk_io'].get('read_bytes_per_sec', 0))
                self._metrics['disk_write'].labels(path='/mnt/storage').set(all_stats['disk_io'].get('write_bytes_per_sec', 0))

            if all_stats.get('network_throughput'):
                self._metrics['net_upload'].set(all_stats['network_throughput'].get('upload_bytes_per_sec', 0))
                self._metrics['net_download'].set(all_stats['network_throughput'].get('download_bytes_per_sec', 0))

            if all_stats.get('docker_stats'):
                self._metrics['docker_total'].set(all_stats['docker_stats'].get('total_containers', 0))
                self._metrics['docker_running'].set(all_stats['docker_stats'].get('running_containers', 0))

            self.log.info("Metrics successfully updated.")
        except Exception as e:
            self.log.error(f"Failed to update metrics: {e}", exc_info=True)