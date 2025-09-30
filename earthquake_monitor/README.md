# earthquake-monitor

`earthquake-monitor` is a Python daemon that periodically fetches earthquake events around your location from multiple public data sources (USGS → EMSC → ISC), normalizes them into a unified format, and when thresholds are met, sends an alert command to an external sound-service over a UNIX socket. Threshold levels (magnitude → melody/duration) are defined in the config.

## Deployment & Running

### Docker (Recommended)

This method handles all dependencies and ensures a consistent environment.

**Prerequisites:**
* `Docker`
* `Docker Compose`

**Instructions:**

**1. Prepare Host Directories (First Time Setup)**
Before the first launch, you must create the directories on the host machine that Docker will use for persistent storage and grant them the necessary permissions.

```bash
# Create directory for the JSON output file and grant permissions
sudo mkdir -p /run/monitors/earthquakes
sudo chmod 777 /run/monitors/earthquakes

# Create directory for logs in your project folder
mkdir -p ./logs
```

**2. Set up the environment**
Copy the production environment template. This file allows you to override default settings if needed.
```bash
cp .env.prod.template .env.prod
# You can edit .env.prod if you need to change intervals, etc.
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

### Native / Legacy Setup

This section details how to run the service directly on the OS.

**Installation**
Install inside your virtual environment or system:
```Bash
cd ~/earthquake_monitor
python3 -m venv .venv_earthquake_monitor
source .venv_earthquake_monitor/bin/activate
pip install -e .
deactivate
```

**Configuration**
The service is configured via environment variables. For native setup, export these variables in your shell or systemd unit file.

| Setting                                  | Default                                      | Purpose                                     |
| ---------------------------------------- | -------------------------------------------- | ------------------------------------------- |
| `LOG_FILE_PATH`                          | `<PROJECT_ROOT>/logs/earthquake_monitor.log` | Rotating file log (10 MB × 5).              |
| `LOCATION_SERVICE_SOCKET`                | `/tmp/location_service.sock`                 | Reads current coordinates (UDS).            |
| `BUZZER_SOCKET`                          | `/tmp/buzzer.sock`                           | Sends sound alert command.                  |
| `DEFAULT_LATITUDE` / `DEFAULT_LONGITUDE` | `38.4237 / 27.1428`                          | Fallback coordinates.                       |
| `SEARCH_RADIUS_KM`                       | `250`                                        | Max search radius.                          |
| `CHECK_INTERVAL_SECONDS`                 | `60`                                         | Loop interval.                              |

**Systemd Integration**
Take the systemd file from here: https://github.com/reekroo/media-server/tree/main/deployment/systemd_services and place it in `/etc/systemd/system/`. Then run:
```bash
sudo systemctl daemon-reload
sudo systemctl enable earthquake-monitor
sudo systemctl start earthquake-monitor
```

**Running Unit Tests**
Install additional dependencies to run async tests:
```bash
# activate your venv
pip install pytest pytest-asyncio
```
Run tests:
```Bash
pytest
```