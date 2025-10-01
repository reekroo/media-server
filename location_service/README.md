# location-service

`location-service` is a lightweight daemon that centralizes geolocation (lat/lon) for local apps.
It periodically resolves your location (via ipinfo.io) with a config-based fallback, and serves the latest coordinates over a UNIX domain socket for fast, local reads.

## Key Features

-   Provider chain with fallback — Tries IpInfoProvider first, then falls back to static coordinates from config if the network API fails.
-   UNIX socket API — Exposes the current location as a small JSON document over a local socket (e.g., `/tmp/location_service.sock`).
-   Periodic refresh — Background thread updates location every `UPDATE_INTERVAL_SECONDS`.
-   Structured, rotating logs — File + console logging with rotation via `concurrent-log-handler`.
-   Simple CLI entrypoint — Run with `location-service`.

---

## Deployment & Running

You can run this service using Docker (recommended) or natively on your system with systemd.

### Docker (Recommended)

This method handles all dependencies and ensures a consistent environment.

**Prerequisites:**
* `Docker`
* `Docker Compose`

**Instructions:**

**1. Prepare Host Directories (First Time Setup)**
Before the first launch, you must create a log directory and grant it the necessary permissions for the container to write into it.
```bash
# Create directory for logs in your project folder and grant permissions
mkdir -p ./logs
sudo chmod 777 ./logs
```

**2. Set up the environment**
Copy the production environment template. This file allows you to override default settings if needed.
```bash
cp .env.prod.template .env.prod
# You can edit .env.prod if you need to change ports, intervals, etc.
```

**3. Build and run the container**
This command will build the Docker image and start the service in the background.
```bash
docker-compose up --build -d
```

**4. Check the logs**
To see the application output or troubleshoot issues, run:
```bash
docker-compose logs -f
```

**5. Stop the application**
To stop and remove the container, run:
```bash
docker-compose down
```

### Systemd (Legacy / Native)

This method requires installing Python and dependencies directly on your system.

**Prerequisites:**
* Python >= 3.9

**1. Installation**
Create a virtual environment and install the project.
```bash
cd /path/to/location-service
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

**2. Systemd Integration**
Take the systemd file from here: https://github.com/reekroo/media-server/tree/main/deployment/systemd_services and place it in `/etc/systemd/system/`.

**3. Enable & Run**
```bash
sudo systemctl daemon-reload
sudo systemctl enable location-service
sudo systemctl start location-service
sudo systemctl status location-service
```

---

## Configuration

The service can be configured via environment variables. The Docker setup uses the `.env.prod` file for this. For native setup, export these variables in your shell or systemd unit file.

| Variable                  | Default                            | Notes                       |
| ------------------------- | ---------------------------------- | --------------------------- |
| `LOG_FILE_PATH`           | `<PROJECT_ROOT>/logs/location.log` | Rotating file log.          |
| `LOCATION_SERVICE_SOCKET` | `/tmp/location_service.sock`       | UNIX socket path.           |
| `UPDATE_INTERVAL_SECONDS` | `3600`                             | Refresh interval (seconds). |
| `DEFAULT_LATITUDE`        | `38.4237`                          | Fallback latitude.          |
| `DEFAULT_LONGITUDE`       | `27.1428`                          | Fallback longitude.         |

---

## Socket API

### Push Socket (Periodic Location)
Endpoint: `LOCATION_SERVICE_SOCKET` (default: `/tmp/location_service.sock`).

**Response:**
```json
{"lat": 38.4237, "lon": 27.1428}
```

### On-Demand Socket (Geocoding)
Endpoint: `ON_DEMAND_GEOCODING_SOCKET` (default: `/tmp/geocoding_service.sock`).

**Request:**
```json
{"city_name": "London"}
```
**Response:**
```json
{"status": "success", "lat": 51.5073, "lon": -0.1277}
```