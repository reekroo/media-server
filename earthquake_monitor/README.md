# earthquake-monitor

`earthquake-monitor` is a Python daemon that periodically fetches earthquake events around your location from multiple public data sources (USGS → EMSC → ISC), normalizes them into a unified format, and when thresholds are met, sends an alert command to an external sound-service over a UNIX socket. Threshold levels (magnitude → melody/duration) are defined in the config.

# Key Features

- Multi-source fallback: Queries USGS, then EMSC, then ISC; merges results and deduplicates events, picking the strongest new event. 

- Flexible location source: Reads from a UNIX socket (location-service) first, falls back to static config coordinates if unavailable. 

- Configurable alert levels: ALERT_LEVELS table maps minimum magnitude to melody, duration, and alert ID. 

- Duplicate protection: Keeps a memory of recently processed event IDs (configurable size). 

- Rotating logs: File + console logging with ConcurrentRotatingFileHandler. 

- Simple CLI: Run as earthquake-monitor. 

# Project Layout

```bash
earthquake-monitor/
├─ src/
│  ├─ main.py                    # entrypoint (wiring)
│  ├─ earthquake_monitor.py      # main loop & alert logic
│  ├─ earthquake_logger.py       # rotating logger
│  ├─ configs.py                 # defaults: thresholds, sockets, intervals
│  ├─ data_sources/              # USGS / EMSC / ISC clients
│  ├─ locations/                 # Socket + Config providers
│  ├─ alerters/                  # SoundAlerter (UNIX socket)
│  └─ models/                    # EarthquakeEvent
└─ pyproject.toml                # dependencies + CLI
```

# Configuration

| Setting                                  | Default                                      | Purpose                                     |
| ---------------------------------------- | -------------------------------------------- | ------------------------------------------- |
| `LOG_FILE_PATH`                          | `<PROJECT_ROOT>/logs/earthquake_monitor.log` | Rotating file log (10 MB × 5).              |
| `LOCATION_SERVICE_SOCKET`                | `/tmp/location_service.sock`                 | Reads current coordinates (UDS).            |
| `BUZZER_SOCKET`                          | `/tmp/buzzer.sock`                           | Sends sound alert command.                  |
| `DEFAULT_LATITUDE` / `DEFAULT_LONGITUDE` | `38.4237 / 27.1428`                          | Fallback coordinates.                       |
| `SEARCH_RADIUS_KM`                       | `250`                                        | Max search radius.                          |
| `CHECK_INTERVAL_SECONDS`                 | `60`                                         | Loop interval.                              |
| `API_TIME_WINDOW_MINUTES`                | `15`                                         | Lookback window for events.                 |
| `MAX_PROCESSED_EVENTS_MEMORY`            | `10`                                         | Number of event IDs kept for deduplication. |
| `ALERT_LEVELS`                           | see `configs.py`                             | Magnitude thresholds → melody/duration/ID.  |
| `MIN_API_MAGNITUDE`                      | derived from `ALERT_LEVELS`                  | Min magnitude used in API queries.          |

# Systemd Integration

Take the systemd file from here: https://github.com/reekroo/media-server/tree/main/deployment/systemd_services

Install inside your virtual environment or system

```bash
pip install .
```

## Enable & Run

```bash
sudo systemctl daemon-reload
sudo systemctl enable metrics-exporter
sudo systemctl start metrics-exporter
```