# location-service

`location-service` is a lightweight daemon that centralizes geolocation (lat/lon) for local apps.
It periodically resolves your location (via ipinfo.io) with a config-based fallback, and serves the latest coordinates over a UNIX domain socket for fast, local reads.

# Key Features

- Provider chain with fallback — Tries IpInfoProvider first, then falls back to static coordinates from config if the network API fails. 

- UNIX socket API — Exposes the current location as a small JSON document over a local socket (e.g., /tmp/location_service.sock). 

- Periodic refresh — Background thread updates location every UPDATE_INTERVAL_SECONDS. 

- Structured, rotating logs — File + console logging with rotation via concurrent-log-handler. 

- Simple CLI entrypoint — Run with location-service.

# Project Structure

```bash
location-service/
├─ src/
│  ├─ main.py                 # entrypoint: wiring, logger, service run
│  ├─ configs.py              # defaults: paths, socket, interval, fallback coords
│  ├─ location_logger.py      # logger setup with rotation
│  ├─ location_controller.py  # background updater + UNIX socket server
│  └─ providers/
│     ├─ base.py              # ILocationProvider interface
│     ├─ ipinfo_provider.py   # IP-based geolocation (ipinfo.io)
│     └─ config_provider.py   # static fallback provider
└─ pyproject.toml
```

# Installation

Requires Python ≥ 3.9. Uses requests and concurrent-log-handler (declared in pyproject.toml).

Install inside your virtual environment or system

```bash
pip install .
```
# Configuration

| Variable / Setting        | Default                            | Notes                        |
| ------------------------- | ---------------------------------- | ---------------------------- |
| `LOG_FILE_PATH`           | `<PROJECT_ROOT>/logs/location.log` | Rotating file log.           |
| `LOG_MAX_BYTES`           | `10 * 1024 * 1024`                 | Rotate size.                 |
| `LOG_BACKUP_COUNT`        | `5`                                | Rotate backups.              |
| `LOG_LEVEL`               | `INFO`                             | Logging level.               |
| `DEFAULT_LATITUDE`        | `38.4237`                          | Fallback latitude.           |
| `DEFAULT_LONGITUDE`       | `27.1428`                          | Fallback longitude.          |
| `LOCATION_SERVICE_SOCKET` | `/tmp/location_service.sock`       | UNIX socket path.            |
| `UPDATE_INTERVAL_SECONDS` | `3600`                             | Refresh interval (seconds).  |

# Systemd Integration

Take the systemd file from here: https://github.com/reekroo/media-server/tree/main/deployment/systemd_services

## Enable & Run

```bash
sudo systemctl daemon-reload
sudo systemctl enable location-service
sudo systemctl start location-service
sudo systemctl status location-service
```

# Socket API

Endpoint: `LOCATION_SERVICE_SOCKET` (default: `/tmp/location_service.sock`). 

## Response (when available):

```json
{"lat": 38.4237, "lon": 27.1428}
```

If no data is ready yet, the service logs a warning and the client may receive nothing (connect early race). 

## Quick Clients

Shell (socat):

```bash
socat - UNIX-CONNECT:/tmp/location_service.sock
```

Python:

```bash
import socket, json
s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.connect("/tmp/location_service.sock")
data = s.recv(4096)
print(json.loads(data))
```