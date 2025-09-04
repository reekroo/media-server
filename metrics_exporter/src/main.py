import time
import sys
import logging

from prometheus_client import start_http_server

import configs
from metrics_logger import setup_logger
from metrics_exporter import PrometheusExporter
from providers.stats_provider import StatsProvider
from providers.system_provider import SystemProvider
from providers.network_provider import NetworkProvider
from providers.disk_provider import DiskProvider
from providers.docker_provider import DockerProvider
from providers.hardware_provider import HardwareProvider

def main():
    log = setup_logger(
        "MetricsExporter",
        configs.LOG_FILE_PATH,
        configs.LOG_LEVEL,
        max_bytes=configs.LOG_MAX_BYTES,
        backup_count=configs.LOG_BACKUP_COUNT
    )
    
    try:
        start_http_server(configs.EXPORTER_PORT)
        log.info(f"Prometheus metrics exporter started on port {configs.EXPORTER_PORT}.")
        
        log.info("Initializing statistics providers...")
        system_provider = SystemProvider(logger=log)
        network_provider = NetworkProvider(logger=log, lan_if=configs.LAN_INTERFACE, wlan_if=configs.WLAN_INTERFACE)
        root_disk_provider = DiskProvider(path=configs.ROOT_DISK_PATH, logger=log)
        storage_disk_provider = DiskProvider(path=configs.STORAGE_DISK_PATH, logger=log)
        docker_provider = DockerProvider(logger=log)
        hardware_provider = HardwareProvider(logger=log)

        stats_provider = StatsProvider(
            system_p=system_provider,
            network_p=network_provider,
            root_disk_p=root_disk_provider,
            storage_disk_p=storage_disk_provider,
            docker_p=docker_provider,
            hardware_p=hardware_provider
        )

        exporter = PrometheusExporter(logger=log)
        
        log.info("Starting metrics collection loop...")
        while True:
            all_stats = stats_provider.get_all_stats()
            exporter.update(all_stats)
            time.sleep(configs.EXPORTER_UPDATE_INTERVAL_SECONDS)

    except Exception as e:
        log.critical(f"Exporter failed critically: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()