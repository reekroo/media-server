import time
import logging
from prometheus_client import start_http_server, Gauge
from src.providers.stats_provider import StatsProvider

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

METRICS = {
    'cpu': Gauge('rpi_cpu_usage_percent', 'Current CPU usage percentage'),
    'cpu_freq': Gauge('rpi_cpu_frequency_mhz', 'Current CPU frequency in MHz'),
    'temp': Gauge('rpi_cpu_temperature_celsius', 'CPU temperature in Celsius'),
    'mem_percent': Gauge('rpi_ram_usage_percent', 'RAM usage percentage'),
    'swap_percent': Gauge('rpi_swap_usage_percent', 'Swap usage percentage'),
    'core_voltage': Gauge('rpi_core_voltage_volts', 'Core voltage of the RPi'),
    'nvme_temp': Gauge('rpi_nvme_temperature_celsius', 'NVMe disk temperature in Celsius'),
    'disk_percent': Gauge('rpi_disk_usage_percent', 'Disk usage percentage', ['path']),
}

def update_metrics(stats_provider):
    try:
        all_stats = stats_provider.get_all_stats()
        
        METRICS['cpu'].set(all_stats.get('cpu', 0))
        METRICS['cpu_freq'].set(all_stats.get('cpu_freq', 0))
        METRICS['temp'].set(all_stats.get('temp', 0))
        METRICS['core_voltage'].set(all_stats.get('core_voltage', 0))
        if 'nvme_health' in all_stats:
            METRICS['nvme_temp'].set(all_stats['nvme_health'].get('temperature', 0))
        
        if 'mem' in all_stats:
            METRICS['mem_percent'].set(all_stats['mem'].get('percent', 0))
        if 'swap' in all_stats:
            METRICS['swap_percent'].set(all_stats['swap'].get('percent', 0))
        
        if 'root_disk_usage' in all_stats:
            METRICS['disk_percent'].labels(path='/').set(all_stats['root_disk_usage'].get('percent', 0))
        
        if 'storage_disk_usage' in all_stats:
            METRICS['disk_percent'].labels(path='/mnt/storage').set(all_stats['storage_disk_usage'].get('percent', 0))
            
        logging.info("Metrics successfully updated.")

    except Exception as e:
        logging.error(f"Failed to update metrics: {e}", exc_info=True)

def run_exporter():
    start_http_server(8001)
    logging.info("Prometheus metrics exporter started on port 8000.")
    
    provider = StatsProvider()
    
    while True:
        update_metrics(provider)
        time.sleep(15)