# metrics-exporter

A lightweight Prometheus exporter for Raspberry Pi that collects system, disk, network, Docker, and hardware stats and exposes them on an HTTP endpoint for scraping (Grafana/Prometheus). It runs a loop at a fixed interval and updates Prometheus Gauges.

# Key features

- HTTP metrics endpoint – starts a Prometheus server (default :8001). 

- Pluggable providers – system, network, disks (root + storage), Docker, hardware/NVMe. 

- Friendly logging – rotating file + console logger. 

- Config via configs.py – log paths, poll interval, interfaces, disk paths, port.

# Installation

Requires Python ≥ 3.9. Uses requests and concurrent-log-handler (declared in pyproject.toml).

Install inside your virtual environment or system

```Bash
cd ~/metrics_exporter
python3 -m venv .venv_metrics_exporter
source .venv_metrics_exporter/bin/activate
pip install -e .
deactivate
```

# Configuration

| Setting                            | Default                     | Notes                                            |
| ---------------------------------- | --------------------------- | ------------------------------------------------ |
| `LOG_FILE_PATH`                    | `logs/metrics_exporter.log` | Rotating logs (10 MB × 5).                       |
| `LOG_LEVEL`                        | `INFO`                      | —                                                |
| `EXPORTER_PORT`                    | `8001`                      | Prometheus `/metrics` port.                      |
| `EXPORTER_UPDATE_INTERVAL_SECONDS` | `15`                        | Poll interval.                                   |
| `ROOT_DISK_PATH`                   | `/`                         | Disk usage gauge label `path="/"`.               |
| `STORAGE_DISK_PATH`                | `/mnt/storage`              | Usage + IO gauges labeled `path="/mnt/storage"`. |
| `LAN_INTERFACE` / `WLAN_INTERFACE` | `eth0` / `wlan0`            | Used for IP + throughput.                        |


# Systemd Integration

Take the systemd file from here: https://github.com/reekroo/media-server/tree/main/deployment/systemd_services

## Enable & Run

```bash
sudo systemctl daemon-reload
sudo systemctl enable metrics-exporter
sudo systemctl start metrics-exporter
```

# Metrics exposed

* rpi_cpu_usage_percent
* rpi_cpu_frequency_mhz
* rpi_cpu_temperature_celsius
* rpi_ram_usage_percent, rpi_swap_usage_percent
* rpi_core_voltage_volts
* rpi_uptime_seconds
* rpi_disk_usage_percent{path="/"|"/mnt/storage"}
* rpi_disk_read_bytes_per_second{path="/mnt/storage"}
* rpi_disk_write_bytes_per_second{path="/mnt/storage"}
* rpi_network_upload_bytes_per_second, rpi_network_download_bytes_per_second
* rpi_docker_containers_total, rpi_docker_containers_running
* rpi_nvme_temperature_celsius