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
pip install -e ./sound_service
pip install -e ./button_service
pip install -e ./oled_service
deactivate
```
* backup_serviсe

```Bash
cd ~/backup_serviсe
python3 -m venv .venv_backup_serviсe
source .venv_backup_serviсe/bin/activate
pip install -e .

#run main script manually to activate google account

python -m src.main

#authenticate as an real user
#provided generated code to the console window
#your pesonal token is generated

deactivate

#for immidiate run the solution use the command from console

sudo /home/reekroo/backup_serviсe/.venv_backup_serviсe/bin/python -m src.main --now
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

* weather_service

```Bash
cd ~/weather_service
python3 -m venv .venv_weather_service
source .venv_weather_service/bin/activate
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

## Backup service

### Service overview

Backup Service is an automated service for creating backups of important directories from your server (e.g., a Raspberry Pi) to Google Drive cloud storage.

Key Features:

* Scheduled Operation: The service runs automatically at a predefined time (e.g., once a week).
* Archiving: Before being sent to the cloud, each specified directory is packed into a separate ZIP archive.
* Multiple Folder Support: You can provide a list of several directories to be backed up.
* Reliability: The service runs in the background as a system service (systemd), restarting automatically in case of failure.
* Logging: All actions and potential errors are recorded in a log file for easy diagnostics.

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

This file contains all the main settings for the service.

* `SOURCE_DIRECTORIES`: The most important parameter. This is a Python list of strings, where each string is the full path to a directory you want to back up.

SOURCE_DIRECTORIES = [
    "/mnt/storage/configs",
    "/home/reekroo/documents"
]

* `TEMP_ARCHIVE_PATH`: The path to a temporary folder where ZIP archives will be created before being uploaded to the cloud. The default is /tmp/backups.

* `SCHEDULE_UNIT`, `SCHEDULE_INTERVAL`, `SCHEDULE_DAY`, `SCHEDULE_TIME`: Parameters for configuring the schedule. By default, the service runs every (INTERVAL=1) week (UNIT=weeks) on Sunday (DAY=sunday) at 03:00 (TIME="03:00").

* `GOOGLE_DRIVE_FOLDER_ID`: The ID of the Google Drive folder you obtained in Step 2.

* `LOG_FILE_PATH`, `LOG_LEVEL`, `LOG_MAX_BYTES`, `LOG_BACKUP_COUNT`: Logging settings. These specify the path to the log file, the level of detail, the maximum file size, and the number of old log files to keep.