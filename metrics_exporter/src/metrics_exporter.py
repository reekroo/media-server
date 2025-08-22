import time

from providers.stats_provider import StatsProvider
from metrics_logger import get_logger
from prometheus_client import Gauge

log = get_logger(__name__)

METRICS = {
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

def update_metrics(stats_provider):
    try:
        all_stats = stats_provider.get_all_stats()
        
        METRICS['cpu_usage'].set(all_stats.get('cpu', 0))
        METRICS['cpu_freq'].set(all_stats.get('cpu_freq', 0))
        METRICS['cpu_temp'].set(all_stats.get('temp', 0))
        METRICS['core_voltage'].set(all_stats.get('core_voltage', 0))
        METRICS['uptime'].set(all_stats.get('uptime', 0))
        
        if all_stats.get('mem'): 
            METRICS['ram_usage'].set(all_stats['mem'].get('percent', 0))
        if all_stats.get('swap'): 
            METRICS['swap_usage'].set(all_stats['swap'].get('percent', 0))
        if all_stats.get('nvme_health'): 
            METRICS['nvme_temp'].set(all_stats['nvme_health'].get('temperature', 0))

        if all_stats.get('root_disk_usage'): 
            METRICS['disk_usage'].labels(path='/').set(all_stats['root_disk_usage'].get('percent', 0))
        if all_stats.get('storage_disk_usage'): 
            METRICS['disk_usage'].labels(path='/mnt/storage').set(all_stats['storage_disk_usage'].get('percent', 0))
            
        if all_stats.get('disk_io'):
            METRICS['disk_read'].labels(path='/mnt/storage').set(all_stats['disk_io'].get('read_bytes_per_sec', 0))
            METRICS['disk_write'].labels(path='/mnt/storage').set(all_stats['disk_io'].get('write_bytes_per_sec', 0))

        if all_stats.get('network_throughput'):
            METRICS['net_upload'].set(all_stats['network_throughput'].get('upload_bytes_per_sec', 0))
            METRICS['net_download'].set(all_stats['network_throughput'].get('download_bytes_per_sec', 0))

        if all_stats.get('docker_stats'):
            METRICS['docker_total'].set(all_stats['docker_stats'].get('total_containers', 0))
            METRICS['docker_running'].set(all_stats['docker_stats'].get('running_containers', 0))

        log.info("Metrics successfully updated.")

    except Exception as e:
        log.error(f"Failed to update metrics: {e}", exc_info=True)