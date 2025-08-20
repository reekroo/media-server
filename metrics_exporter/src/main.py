import time

from prometheus_client import start_http_server
from src.metrics_logger import get_logger
from src.metrics_exporter import update_metrics
from src.providers.stats_provider import StatsProvider
from src.configs import EXPORTER_PORT, EXPORTER_UPDATE_INTERVAL_SECONDS

log = get_logger(__name__)

def main():
    start_http_server(EXPORTER_PORT)
    log.info(f"Prometheus metrics exporter started on port {EXPORTER_PORT}.")
    
    provider = StatsProvider()
    
    while True:
        update_metrics(provider)
        time.sleep(EXPORTER_UPDATE_INTERVAL_SECONDS)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        get_logger(__name__).critical(f"Exporter failed critically: {e}", exc_info=True)
        exit(1)