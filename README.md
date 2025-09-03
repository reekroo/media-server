<details>
    <summary>Table of Contents</summary>
    <ol>
        <li><a href="#raspberry-pi-5-media-server-setup">Raspberry Pi 5 Media Server Setup</a></li>
        <li>
        <a href="#1-preparation-and-initial-setup-%EF%B8%8F">1. Preparation and Initial Setup</a>
            <ul>
                <li><a href="#operating-system-installation">Operating System Installation</a></li>
                <li><a href="#ssh-connection">SSH Connection</a></li>
                <li><a href="#copying-files-and-system-update">Copying Files and System Update</a></li>
            </ul>
        </li>
        <li>
            <a href="#2-nvme-drive-preparation-">2. NVMe Drive Preparation</a>
            <ul>
                <li><a href="#enabling-pcie-gen3">Enabling PCIe Gen3</a></li>
                <li><a href="#partitioning-and-formatting-the-drive">Partitioning and Formatting the Drive</a></li>
                <li><a href="#mounting-the-drive">Mounting the Drive</a></li>
            </ul>
        </li>
        <li>
            <a href="#software-installation-and-services-%EF%B8%8F">3. Software Installation and Services</a>
            <ul>
                <li><a href="#docker--portainer-installation">Docker & Portainer Installation</a></li>
                <li><a href="#setting-up-python-virtual-environments-venv">Setting Up Python Virtual Environments (venv)</a></li>
                <li><a href="#samba-setup-network-storage-access">Samba Setup (Network Storage Access)</a></li>
                <li><a href="#activating-the-i2c-interface">Activating the I2C Interface</a></li>
            </ul>
        </li>
        <li>
            <a href="#4-starting-system-services-">4. Starting System Services</a>
            <ul>
                <li><a href="#services">Services</a></li>
                <li><a href="#peripherals">Peripherals</a></li>
            </ul>
        </li>
        <li>
            <a href="#5-utilities-and-troubleshooting-%EF%B8%8F">5. Utilities and Troubleshooting</a>
            <ul>
                <li><a href="#running-unit-tests">Running Unit Tests</a></li>
                <li><a href="#system-time-synchronization">System Time Synchronization</a></li>
                <li><a href="#increasing-the-swap-file-size">Increasing the Swap File Size</a></li>
            </ul>
        </li>
    </ol>
</details>

# Raspberry Pi 5 Media Server Setup

This document is a step-by-step guide for setting up a media server on a Raspberry Pi 5 using an NVMe drive. The guide covers the initial OS installation, disk preparation, Docker and Samba installation, as well as starting and managing system services.

## Operating System Installation

1. Download and install the Raspberry Pi Imager.
2. Select and flash the Raspberry Pi OS Lite (64-bit) image for the Pi 5 to your SSD.

## SSH Connection

After installing the OS and connecting the Pi to your network, find its IP address and connect via SSH.

```Bash
ssh reekroo@192.168.0.118
```

⚠️ If you encounter any issues with the SSH key, remove the old key from your known hosts.

```Bash
ssh-keygen -R 192.168.0.118
```

## Update system

Update your Pi's packages and firmware.

```Bash
sudo apt update
sudo apt upgrade -y
```

# Hardwere Setup

TODO

# Initial Setup

## NVMe Drive Preparation

### Enabling PCIe Gen3

To improve the performance of your NVMe drive, you need to enable PCIe Gen3.

1. Open the configuration file:

```Bash
sudo nano /boot/firmware/config.txt
```

2. Add the following line to the end of the file:

```Ini, TOML
dtparam=pcie_gen=3
```

### Partitioning and Formatting the Drive

1. Check if the drive is recognized by the system:

```Bash
lsblk
```

2. Run the disk partitioning utility. Be careful, as this will erase all data on the drive!

```Bash
sudo fdisk /dev/nvme0n1
```

* `g` - create a new empty GPT partition table.
* `n` - create a new partition.
* [Enter] - select the default partition number.
* [Enter] - select the default first sector.
* [Enter] - select the default last sector.
* `w`- write the changes to the disk and exit.

3. Format the new partition with the `ext4` filesystem.

```Bash
sudo mkfs.ext4 /dev/nvme0n1p1
```

### Mounting the Drive

To ensure the drive mounts automatically on boot, add it to `/etc/fstab`.

1. Create a mount point:

```Bash
sudo mkdir /mnt/storage
```

2. Find the UUID of your partition:

```Bash
sudo blkid /dev/nvme0n1p1
```

3. Edit the `fstab ` file:

```Bash
sudo nano /etc/fstab
```

Add the following line to the end of the file, replacing the UUID with the one you obtained in the previous step:

```Ini, TOML
UUID="581ac755-4d7a-4fe6-bf3e-9102d81e4458" /mnt/storage ext4 defaults,auto,users,rw,nofail 0 0
```

4. Apply the changes and set permissions.

```Bash
sudo mount -a
sudo chown -R reekroo:reekroo /mnt/storage
sudo chmod -R 777 /mnt/storage
```

## Activating the I2C Interface

This step is required for peripherals like I2C OLED displays.

```Bash
sudo raspi-config
```

* `Interface Options` -> `I5 I2C` -> `Yes`
* `Ok` -> `Finish`

## Activating the SPI Interface

This step is required for peripherals like SPI OLED displays.

```Bash
sudo raspi-config
```

* `Interface Options` -> `I4 SPI` -> `Yes`
* `Ok` -> `Finish`

## [Optional] Increasing the Swap File Size

If you need more virtual memory, you can increase the size of the swap file.

1. Check the current swap size:

```Bash
htop
sudo swapon --show
```

2. Disable, create, and enable a new 2GB swap file:

```Bash
sudo swapoff /var/swap
sudo fallocate -l 2G /var/swapfile
sudo mkswap /var/swapfile
sudo chmod 600 /var/swapfile
sudo swapon /var/swapfile
sudo swapon --show
htop
```

3. To make this change persistent across reboots, edit the /etc/dphys-swapfile file and set CONF_SWAPSIZE to 2048.

```Bash
sudo nano /etc/dphys-swapfile
```

```Ini, TOML
# Set the swap file size
CONF_SWAPSIZE=2048
```

4. Apply the changes from the configuration file.

```Bash
sudo dphys-swapfile swapoff
sudo dphys-swapfile swapon
htop
```

## [Optional] System Time Synchronization

Check and set your system's timezone.

```Bash
date
sudo timedatectl set-timezone Europe/Istanbul
date
timedatectl status
```

# Software Installation and Services

## Copying Files and System Update

To synchronize local script files, you can use `VS Code` with the `SFTP` plugin or a similar tool.

⚠️ Important Security Note: The `sudo chmod -R 777` command grants full permissions to all users and is not recommended for permanent use due to security risks. Use it cautiously and only for temporary setup tasks.

```Bash
cd /etc/systemd/system
sudo chmod -R 777 .
```

Update your Pi's packages and firmware.

```Bash
sudo apt update
sudo apt upgrade -y
sudo rpi-eeprom-update -a
sudo apt install socat
```

## Setting Up Python Virtual Environments (venv)

It is recommended to use a separate virtual environment for each project.

* peripheral_scripts

```Bash
cd ~/peripheral_scripts
python3 -m venv .venv_peripherals
source .venv_peripherals/bin/activate
pip install -e ./common_utils
pip install -e ./network_policy
pip install -e ./bluetooth_policy
pip install -e ./sound_service
pip install -e ./button_service
pip install -e ./oled_service
pip install -e ./ups_service
deactivate
```
* backup_service

```Bash
cd ~/backup_service
python3 -m venv .venv_backup_service
source .venv_backup_service/bin/activate
pip install -e .

#run main script manually to activate google account

python -m src.main

#authenticate as an real user
#provided generated code to the console window
#your pesonal token is generated

deactivate

#for immidiate run the solution use the command from console

sudo /home/reekroo/backup_service/.venv_backup_service/bin/python -m src.main --now
```

* location_service

```Bash
cd ~/location_service
python3 -m venv .venv_location_service
source .venv_location_service/bin/activate
pip install -e .
deactivate
```

* earthquake_monitor

```Bash
cd ~/earthquake_monitor
python3 -m venv .venv_earthquake_monitor
source .venv_earthquake_monitor/bin/activate
pip install -e .
deactivate
```

* weather_monitor

```Bash
cd ~/weather_monitor
python3 -m venv .venv_weather_monitor
source .venv_weather_monitor/bin/activate
pip install -e .
deactivate
```

* metrics_exporter

```Bash
cd ~/metrics_exporter
python3 -m venv .venv_metrics_exporter
source .venv_metrics_exporter/bin/activate
pip install -e .
deactivate
```

## Starting System Services

Once all scripts are copied and virtual environments are set up, you can enable the systemd services.

### Services

1. Reload the systemd manager configuration:

```Bash
sudo systemctl daemon-reload
```

2. Enable and start the services immediately:

```Bash
sudo systemctl enable --now sound-controller.service
sudo systemctl enable --now oled-status.service
sudo systemctl enable --now button-manager.service
sudo systemctl enable --now ups-service.service
sudo systemctl enable --now location-monitor.service
sudo systemctl enable --now earthquake-monitor.service
sudo systemctl enable --now weather-monitor.service
sudo systemctl enable --now metrics-exporter.service
sudo systemctl enable --now backup.service
```

3. Check the status of the running services:

```Bash
sudo systemctl status sound-controller.service
sudo systemctl status oled-status.service
sudo systemctl status button-manager.service
sudo systemctl status ups-service.service
sudo systemctl status location-monitor.service
sudo systemctl status earthquake-monitor.service
sudo systemctl status weather-monitor.service
sudo systemctl status metrics-exporter.service
sudo systemctl status backup.service
```

ℹ️ To view real-time logs for a specific service, use:
`journalctl -u <service_name> -n 20 -f`

ℹ️ To logs in files:
`tail -f <path_to_log_file>`

ℹ️ To restart a service, use:
`sudo systemctl restart <service_name>`

ℹ️ To stop a service, use:
`sudo systemctl stop <service_name>`

### Peripherals

Enable additional services for power management and networking.

```Bash
sudo systemctl enable sound-boot.service
sudo systemctl enable sound-shutdown.service
sudo systemctl enable nvme-powermode-manager.service
sudo systemctl enable wifi-lan-manager.service
sudo systemctl enable bluetooth-manager.service
```

⚠️ The `nvme-powermode-manager.service` requires `nvme-cli` to be installed.
`sudo apt update`
`sudo apt install nvme-cli`

### Running Unit Tests

To verify the functionality of your scripts, navigate to the project directory and run the tests.

```Bash
cd ~/earthquake_monitor
source .venv_earthquake_monitor/bin/activate
python3 -m unittest discover -s tests -p "test_*.py"
```

```Bash
cd ~/earthquake_monitor
source .venv_earthquake_monitor/bin/activate
python3 -m tests.integration_test_alert
```

## Docker & Portainer Installation

1. Install Docker:

```Bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

2. Add your user to the docker group to run Docker commands without sudo.

```Bash
sudo usermod -aG docker $USER
sudo usermod -aG docker reekroo
sudo reboot
```

3. Install the Docker Compose plugin:

```Bash
sudo apt-get install docker-compose-plugin
```

4. Create a volume and run the Portainer container.

```Bash
docker volume create portainer_data
docker run -d -p 8000:8000 -p 9443:9443 --name portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce:latest
```

5. Navigate to your Docker stacks directory and start them.

```Bash
cd ~/docker_stacks
make up
```

# Service setup

his document describes the core system services running on the Raspberry Pi media-server environment. Each section explains the purpose of the service, its key features, initial setup, and configuration parameters.

## Backup service

Backup Servic**Backup Service** automates periodic backups of specified directories to **Google Drive**.  
Each selected directory is archived (ZIP) to a temporary location and then uploaded to your Drive; logs are written with rotation for reliability. :contentReference[oaicite:0]{index=0} :contentReference[oaicite:1]{index=1} :contentReference[oaicite:2]{index=2}

**Key capabilities:**
- **Scheduled execution** (weekly by default) with a simple, readable scheduler. :contentReference[oaicite:3]{index=3}
- **Per-directory archiving** into `.zip` before upload. :contentReference[oaicite:4]{index=4}
- **Google Drive upload** with OAuth2 (token refresh + console auth flow fallback). :contentReference[oaicite:5]{index=5}
- **Isolated temp storage** and **cleanup** of temporary archives after upload. :contentReference[oaicite:6]{index=6}
- **Logging with rotation** via `ConcurrentRotatingFileHandler`. :contentReference[oaicite:7]{index=7}

### Google Account Setup

To work, the service needs permission to access your Google Drive. This is a one-time setup.

1. Step 1: Obtaining `credentials.json`
This file is the key that allows your application to request access to the Google API.

* Go to the [Google Cloud Console](https://console.cloud.google.com/) and create a new project.
* In the navigation menu (☰), open "APIs & Services" -> "Library". Find the "Google Drive API" and enable it (click the Enable button).
* Return to "APIs & Services" and go to the "Credentials" section.
* Click "+ CREATE CREDENTIALS" -> "OAuth client ID".
* For "Application type," select "Desktop app" and give it a name (e.g., "Backup Service").
* After creation, click "DOWNLOAD JSON". Rename the downloaded file to `credentials.json` and place it in the root folder of your project.

2. Step 2: Obtaining `GOOGLE_DRIVE_FOLDER_ID`. 
This is the ID of the folder on your Google Drive where the archives will be uploaded.

* Create or select a folder on [Google Drive](https://drive.google.com/).
* Open it. The ID will be at the end of the URL in your browser's address bar.
Example: https://drive.google.com/drive/folders/1a2b3c4d5e6f7g8h9i0j
Your ID here is: 1a2b3c4d5e6f7g8h9i0j.

### Configuration Breakdown (src/configs.py)

| Parameter | Description | Default / Notes |
|---|---|---|
| `SOURCE_DIRECTORIES` | List of directories to back up. Can be overridden via `BACKUP_SOURCE_DIR` env var. | `["/mnt/storage/configs"]` (by default one path) :contentReference[oaicite:12]{index=12} |
| `TEMP_ARCHIVE_PATH` | Staging folder for creating ZIPs. Auto-created at startup. | `/tmp/backups` (overridable by `BACKUP_TEMP_PATH`) :contentReference[oaicite:13]{index=13} |
| `SCHEDULE_UNIT` | Time unit for schedule. | `"weeks"` (supported: `weeks`, `days`) :contentReference[oaicite:14]{index=14} :contentReference[oaicite:15]{index=15} |
| `SCHEDULE_INTERVAL` | Interval count. | `1` (every 1 week/day) :contentReference[oaicite:16]{index=16} |
| `SCHEDULE_DAY` | Day of week for weekly schedule. | `"sunday"` :contentReference[oaicite:17]{index=17} |
| `SCHEDULE_TIME` | Local time to run. | `"03:00"` :contentReference[oaicite:18]{index=18} |
| `GOOGLE_DRIVE_FOLDER_ID` | Destination folder ID on Google Drive. | From env or config default. :contentReference[oaicite:19]{index=19} |
| `CREDENTIALS_FILE_PATH` | Expected path to `credentials.json`. | `<project_root>/credentials.json` :contentReference[oaicite:20]{index=20} |
| `TOKEN_FILE_PATH` | Where OAuth token is stored. | `<project_root>/token.json` :contentReference[oaicite:21]{index=21} |
| `SCOPES` | OAuth scopes for Drive. | `['https://www.googleapis.com/auth/drive.file']` :contentReference[oaicite:22]{index=22} |
| `LOG_FILE_PATH` | Log file location. | `<project_root>/logs/backup_serviсe.log` :contentReference[oaicite:23]{index=23} |
| `LOG_LEVEL` / `LOG_MAX_BYTES` / `LOG_BACKUP_COUNT` | Logging verbosity & rotation. | `INFO`, `5 MB`, `3` :contentReference[oaicite:24]{index=24} |

### Run immediately (one-shot)
```bash
#first variant
cd ~/backup_serviсe
sudo /home/reekroo/backup_serviсe/.venv_backup_serviсe/bin/python -m src.main --now

#second variant
cd ~/backup_serviсe
source .venv_backup_serviсe/bin/activate
python -m backup_service.main --now
```

## Locatıon Service

**Location Service** is a background system daemon that determines and maintains the current geographic location of the server (e.g., Raspberry Pi).  
It periodically updates location data from external and fallback providers, and exposes this information to other applications via a Unix socket.

**Key features:**
- **Multiple providers**:  
  - Primary: `IpInfoProvider` (queries [ipinfo.io](https://ipinfo.io) for location based on external IP).  
  - Fallback: `ConfigFallbackProvider` (uses predefined coordinates from configuration).
- **Automatic updates**: Location is refreshed at regular intervals (default: once per hour).
- **Inter-process communication**: Other local services can connect to `/tmp/location_service.sock` to retrieve the latest location data in JSON format.
- **Threaded execution**: Separate threads for location updates and socket communication.
- **Logging with rotation**: Structured logs are written to `logs/location.log` and printed to console.

### Initial Setup

- No external configuration is required beyond network access.  
- By default, the service will attempt to fetch location data via `ipinfo.io`.  
- If that fails (e.g., offline, blocked, or API unavailable), it falls back to the default coordinates in `configs.py`.

**Optional:**  
- Ensure outbound HTTPS traffic is allowed to `ipinfo.io`.  
- Adjust default latitude/longitude in `configs.py` to match your actual fallback location.

### Configuration (src/configs.py)

| Parameter                 | Description                                                            | Default Value                  |
|---------------------------|------------------------------------------------------------------------|--------------------------------|
| `LOG_FILE_PATH`           | Path to log file                                                       | `logs/location.log` :contentReference[oaicite:0]{index=0} |
| `LOG_MAX_BYTES`           | Max log file size before rotation (bytes)                              | `10 * 1024 * 1024` (10 MB) :contentReference[oaicite:1]{index=1} |
| `LOG_BACKUP_COUNT`        | Number of rotated log files to keep                                    | `5` :contentReference[oaicite:2]{index=2} |
| `DEFAULT_LATITUDE`        | Fallback latitude if no provider succeeds                              | `38.4237` :contentReference[oaicite:3]{index=3} |
| `DEFAULT_LONGITUDE`       | Fallback longitude if no provider succeeds                             | `27.1428` :contentReference[oaicite:4]{index=4} |
| `LOCATION_SERVICE_SOCKET` | Unix socket path for client connections                                | `/tmp/location_service.sock` :contentReference[oaicite:5]{index=5} |
| `UPDATE_INTERVAL_SECONDS` | Interval between location updates                                      | `3600` (1 hour) :contentReference[oaicite:6]{index=6} |

## Weather Monitor

**Weather Service** periodically determines the device’s location, fetches current weather from online providers, and publishes the result through one or more outputs (console and/or a local Unix socket). It runs continuously with logging and safe shutdown. :contentReference[oaicite:0]{index=0} :contentReference[oaicite:1]{index=1}

**Key capabilities:**
- **Multiple weather providers with fallback**: OpenWeatherMap → WeatherAPI. :contentReference[oaicite:2]{index=2} :contentReference[oaicite:3]{index=3}
- **Location resolution with fallback**: Location Service socket → local config defaults. :contentReference[oaicite:4]{index=4}
- **Pluggable outputs**: console and/or Unix socket (`/tmp/weather_service.sock`). :contentReference[oaicite:5]{index=5}
- **Configurable polling interval** with clean shutdown and output closing. :contentReference[oaicite:6]{index=6}
- **Rotating logs** stored under `logs/`. :contentReference[oaicite:7]{index=7}

### Initial setup

- Ensure outbound network access for the chosen weather APIs.
- Provide API keys via environment variables **`OPENWEATHERMAP_API_KEY`** and **`WEATHERAPI_API_KEY`** (do **not** hardcode keys). :contentReference[oaicite:8]{index=8}
- If your **Location Service** is running, it will be used first via `/tmp/location_service.sock`; otherwise the service falls back to coordinates from config. :contentReference[oaicite:9]{index=9} :contentReference[oaicite:10]{index=10}

### Configuration (src/configs.py)

| Key | Meaning | Default / Notes |
|---|---|---|
| `LOG_FILE_PATH` | Log file path | `logs/weather_service.log` :contentReference[oaicite:11]{index=11} |
| `LOG_MAX_BYTES`, `LOG_BACKUP_COUNT` | Log rotation | `10MB`, `5` :contentReference[oaicite:12]{index=12} |
| `WEATHER_SERVICE_SOCKET` | Output socket (Unix) | `/tmp/weather_service.sock` :contentReference[oaicite:13]{index=13} |
| `LOCATION_SERVICE_SOCKET` | Location Service socket | `/tmp/location_service.sock` :contentReference[oaicite:14]{index=14} |
| `OPENWEATHERMAP_API_KEY` | OWM API key (from env) | `os.getenv("OPENWEATHERMAP_API_KEY", ...)` :contentReference[oaicite:15]{index=15} |
| `WEATHERAPI_API_KEY` | WeatherAPI key (from env) | `os.getenv("WEATHERAPI_API_KEY", ...)` :contentReference[oaicite:16]{index=16} |
| `DEFAULT_LATITUDE`, `DEFAULT_LONGITUDE` | Fallback location | `38.4237`, `27.1428` :contentReference[oaicite:17]{index=17} |
| `INTERVAL_SECONDS` | Polling interval | `1800` (30 min) :contentReference[oaicite:18]{index=18} |
| `OUTPUT_MODES` | Enabled outputs | `['console','socket']` (order matters) :contentReference[oaicite:19]{index=19} |

## Weather Monitor

**Earthquake Monitor** periodically polls multiple earthquake feeds (USGS, EMSC, ISC), filters events around the device’s location, and triggers an audible alert via the sound/buzzer socket based on configurable severity levels. It deduplicates already-processed events and runs continuously with rotating logs. :contentReference[oaicite:0]{index=0} :contentReference[oaicite:1]{index=1} :contentReference[oaicite:2]{index=2} :contentReference[oaicite:3]{index=3}

**Key capabilities**
- **Multiple data sources with fallback/merge**: USGS → EMSC → ISC (new events from all sources are combined). :contentReference[oaicite:4]{index=4}
- **Location resolution with fallback**: Location Service socket → local config defaults. :contentReference[oaicite:5]{index=5} :contentReference[oaicite:6]{index=6}
- **Alert levels (1–5)** with thresholds, durations, melodies. First matching level (from highest to lowest) is used. :contentReference[oaicite:7]{index=7}
- **Deduplication** using a sliding window of recent event IDs to avoid repeat alerts. :contentReference[oaicite:8]{index=8}
- **Logging with rotation** to `logs/earthquake_monitor.log`. :contentReference[oaicite:9]{index=9}

### Initial setup

- Ensure outbound HTTPS access to USGS/EMSC/ISC APIs. :contentReference[oaicite:10]{index=10} :contentReference[oaicite:11]{index=11} :contentReference[oaicite:12]{index=12}
- If the **Location Service** is running, it will be used first via `/tmp/location_service.sock`; otherwise the monitor falls back to configured coordinates. :contentReference[oaicite:13]{index=13} :contentReference[oaicite:14]{index=14}
- Make sure the **sound/buzzer** service is available at `/tmp/buzzer.sock` so alerts can be played. :contentReference[oaicite:15]{index=15} :contentReference[oaicite:16]{index=16}

### Configuration (src/configs.py)

| Key | Meaning | Default / Notes |
|---|---|---|
| `LOG_FILE_PATH`, `LOG_MAX_BYTES`, `LOG_BACKUP_COUNT` | Log path & rotation | `logs/earthquake_monitor.log`, `10MB`, `5` :contentReference[oaicite:17]{index=17} |
| `LOCATION_SERVICE_SOCKET` | Path to Location Service socket | `/tmp/location_service.sock` :contentReference[oaicite:18]{index=18} |
| `BUZZER_SOCKET` | Path to sound/buzzer socket | `/tmp/buzzer.sock` :contentReference[oaicite:19]{index=19} |
| `DEFAULT_LATITUDE`, `DEFAULT_LONGITUDE` | Fallback coordinates | `38.4237`, `27.1428` :contentReference[oaicite:20]{index=20} |
| `SEARCH_RADIUS_KM` | Search radius around location | `250` km :contentReference[oaicite:21]{index=21} |
| `CHECK_INTERVAL_SECONDS` | Poll interval | `60` seconds :contentReference[oaicite:22]{index=22} |
| `API_TIME_WINDOW_MINUTES` | How far back to look for events | `15` minutes :contentReference[oaicite:23]{index=23} |
| `MAX_PROCESSED_EVENTS_MEMORY` | Dedup window (IDs kept) | `10` (used to size the deque) :contentReference[oaicite:24]{index=24} |
| `ALERT_LEVELS` | Levels 1–5 with thresholds, durations, melodies | See inline list in `configs.py` (3.5→10s … 7.0→180s) :contentReference[oaicite:25]{index=25} |
| `MIN_API_MAGNITUDE` | Derived minimum magnitude for API queries | `min(level.min_magnitude)` from `ALERT_LEVELS` :contentReference[oaicite:26]{index=26} |

## Metrics Exporter

**Metrics Exporter** exposes Raspberry Pi system and stack metrics via an HTTP endpoint in **Prometheus** format.  
It periodically gathers stats (CPU, memory, disks, network, Docker, NVMe, voltage, etc.) and updates Prometheus **Gauges** that are scraped by Prometheus/Grafana. :contentReference[oaicite:0]{index=0} :contentReference[oaicite:1]{index=1}

**Key capabilities**
- Built-in HTTP server for `/metrics` on a configurable port. :contentReference[oaicite:2]{index=2}
- Rich metric set (CPU, temp, RAM, swap, uptime, disk usage & I/O, network throughput, Docker containers, NVMe temp, core voltage). :contentReference[oaicite:3]{index=3}
- Rotating logs with file + stdout handlers. :contentReference[oaicite:4]{index=4}

### Initial setup

- Open/allow the exporter port on localhost (default **8001**). :contentReference[oaicite:5]{index=5}
- Ensure the `/mnt/storage` mount exists if you want disk usage and I/O metrics for that path (labels use `/mnt/storage`). :contentReference[oaicite:6]{index=6}
- Prometheus server must be able to scrape the exporter’s address (see config example below).  
- Optional but recommended: run as a `systemd` service for auto-restart.

### Configuration (src/configs.py)

| Key | Meaning | Default |
|---|---|---|
| `LOG_FILE_PATH` | Path to log file | `logs/metrics_exporter.log` :contentReference[oaicite:7]{index=7} |
| `LOG_MAX_BYTES` / `LOG_BACKUP_COUNT` | Log rotation settings | `10MB` / `5` :contentReference[oaicite:8]{index=8} |
| `EXPORTER_PORT` | HTTP port for `/metrics` | `8001` :contentReference[oaicite:9]{index=9} |
| `EXPORTER_UPDATE_INTERVAL_SECONDS` | Collection interval | `15` seconds :contentReference[oaicite:10]{index=10} |

### Metrics exposed

| Metric name | Type | Labels | Source field | Description |
|---|---|---|---|---|
| `rpi_cpu_usage_percent` | Gauge | — | `cpu` | CPU usage % :contentReference[oaicite:14]{index=14} |
| `rpi_cpu_frequency_mhz` | Gauge | — | `cpu_freq` | CPU frequency (MHz) :contentReference[oaicite:15]{index=15} |
| `rpi_cpu_temperature_celsius` | Gauge | — | `temp` | CPU temperature (°C) :contentReference[oaicite:16]{index=16} |
| `rpi_ram_usage_percent` | Gauge | — | `mem.percent` | RAM usage % :contentReference[oaicite:17]{index=17} |
| `rpi_swap_usage_percent` | Gauge | — | `swap.percent` | Swap usage % :contentReference[oaicite:18]{index=18} |
| `rpi_core_voltage_volts` | Gauge | — | `core_voltage` | Core voltage (V) :contentReference[oaicite:19]{index=19} |
| `rpi_uptime_seconds` | Gauge | — | `uptime` | System uptime (s) :contentReference[oaicite:20]{index=20} |
| `rpi_disk_usage_percent` | Gauge | `path` | `root_disk_usage.percent`, `storage_disk_usage.percent` | Disk usage % per path (`/`, `/mnt/storage`) :contentReference[oaicite:21]{index=21} |
| `rpi_disk_read_bytes_per_second` | Gauge | `path` | `disk_io.read_bytes_per_sec` | Disk read B/s (for `/mnt/storage`) :contentReference[oaicite:22]{index=22} |
| `rpi_disk_write_bytes_per_second` | Gauge | `path` | `disk_io.write_bytes_per_sec` | Disk write B/s (for `/mnt/storage`) :contentReference[oaicite:23]{index=23} |
| `rpi_network_upload_bytes_per_second` | Gauge | — | `network_throughput.upload_bytes_per_sec` | Network upload B/s :contentReference[oaicite:24]{index=24} |
| `rpi_network_download_bytes_per_second` | Gauge | — | `network_throughput.download_bytes_per_sec` | Network download B/s :contentReference[oaicite:25]{index=25} |
| `rpi_docker_containers_total` | Gauge | — | `docker_stats.total_containers` | Total Docker containers :contentReference[oaicite:26]{index=26} |
| `rpi_docker_containers_running` | Gauge | — | `docker_stats.running_containers` | Running Docker containers :contentReference[oaicite:27]{index=27} |
| `rpi_nvme_temperature_celsius` | Gauge | — | `nvme_health.temperature` | NVMe temperature (°C) :contentReference[oaicite:28]{index=28} |

### Running the service - One-shot (foreground)
```bash
python -m metrics_exporter.main
```