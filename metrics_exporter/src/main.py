import logging
from src.metrics_exporter import run_exporter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == '__main__':
    try:
        run_exporter()
    except Exception as e:
        logging.critical(f"Exporter failed critically: {e}")
        exit(1)