# metrics-exporter

A lightweight Prometheus exporter for Raspberry Pi that collects system, disk, network, Docker, and hardware stats and exposes them on an HTTP endpoint for scraping (Grafana/Prometheus).

## Deployment

### Docker (Recommended)

This method encapsulates all dependencies and provides the necessary host access for metric collection.

**Prerequisites:**
* `Docker`
* `Docker Compose`

**Instructions:**

**1. Prepare Host Directories**
Create a directory for the service's logs.
```bash
mkdir -p ./logs
```

**2. Set up the environment**
Copy the production environment template.
```bash
cp .env.prod.template .env.prod
# You can edit .env.prod to change ports, intervals, or disk paths.
```

**3. Build and run the container**
```bash
docker-compose up --build -d
```
The exporter will now be available at `http://<your-pi-ip>:8001/metrics`.

**4. Check the logs**
```bash
docker-compose logs -f
```

**5. Stop the application**
```bash
docker-compose down
```

### Native / Legacy Setup

Requires Python ≥ 3.9. See `pyproject.toml` for dependencies.

**Installation**
```Bash
cd ~/metrics_exporter
python3 -m venv .venv_metrics_exporter
source .venv_metrics_exporter/bin/activate
pip install -e .
```

**Systemd Integration**
Use a systemd unit file to manage the service. See example here: https://github.com/reekroo/media-server/tree/main/deployment/systemd_services

**Enable & Run**
```bash
sudo systemctl daemon-reload
sudo systemctl enable metrics-exporter
sudo systemctl start metrics-exporter
```

---

## Configuration

The service is configured via environment variables. The Docker setup uses the `.env.prod` file for this. For native setup, export these variables in your shell or systemd unit file.

| Setting                            | Default                     | Notes                                            |
| ---------------------------------- | --------------------------- | ------------------------------------------------ |
| `LOG_FILE_PATH`                    | `logs/metrics_exporter.log` | Rotating logs (10 MB × 5).                       |
| `LOG_LEVEL`                        | `INFO`                      | —                                                |
| `EXPORTER_PORT`                    | `8001`                      | Prometheus `/metrics` port.                      |
| `EXPORTER_UPDATE_INTERVAL_SECONDS` | `15`                        | Poll interval.                                   |
| `ROOT_DISK_PATH`                   | `/`                         | Disk usage gauge label `path="/"`.               |
| `STORAGE_DISK_PATH`                | `/mnt/storage`              | Usage + IO gauges labeled `path="/mnt/storage"`. |
| `LAN_INTERFACE` / `WLAN_INTERFACE` | `eth0` / `wlan0`            | Used for IP + throughput.                        |

---

## Metrics Exposed

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