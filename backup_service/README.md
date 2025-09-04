# location-service

`backup-service` creates timestamped ZIP archives of your configured directories and uploads them to Google Drive on a schedule (or immediately with a flag). It logs all actions with rotation and cleans up temporary archives after a successful upload.

# Key Features

- Zip archiving using a pluggable archiver (Zipper, format: zip). 

- Google Drive upload with OAuth2; token is cached to token.json. 

- Config-driven sources & schedule (weekly/daily). 

- Rotating logs (file + console) via concurrent-log-handler. 

- CLI entrypoint backup-service with --now to run once and exit.

# Installation

Requires Python ≥ 3.9. Uses requests and concurrent-log-handler (declared in pyproject.toml).

Install inside your virtual environment or system

```bash
pip install .
```

# Google Account Setup

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

# Configuration

| Setting / Env                                                            | Default                      | Purpose                                                     |
| ------------------------------------------------------------------------ | ---------------------------- | ----------------------------------------------------------- |
| `SOURCE_DIRECTORIES` / `BACKUP_SOURCE_DIR`                               | `/mnt/storage/configs`       | Directories to back up (list in code or single env var).    |
| `TEMP_ARCHIVE_PATH` / `BACKUP_TEMP_PATH`                                 | `/tmp/backups`               | Where ZIPs are created before upload.                       |
| `GOOGLE_DRIVE_FOLDER_ID`                                                 | `1m7GaT…uun46`               | Destination folder in Drive.                                |
| `CREDENTIALS_FILE_PATH`                                                  | `./credentials.json`         | OAuth client secrets (download from Google Cloud Console).  |
| `TOKEN_FILE_PATH`                                                        | `./token.json`               | Saved OAuth token (created on first auth).                  |
| `SCOPES`                                                                 | `drive.file`                 | Minimal scope used for upload.                              |
| `LOG_FILE_PATH`                                                          | `./logs/backup_service.log`  | Rotating file log path.                                     |
| `LOG_LEVEL`, `LOG_MAX_BYTES`, `LOG_BACKUP_COUNT`                         | `INFO`, `5MB`, `3`           | Logging/rotation config.                                    |
| `SCHEDULE_UNIT` / `SCHEDULE_INTERVAL` / `SCHEDULE_DAY` / `SCHEDULE_TIME` | `weeks / 1 / sunday / 03:00` | When to run (supports weekly/day-based modes).              |


# Systemd Integration

Take the systemd file from here: https://github.com/reekroo/media-server/tree/main/deployment/systemd_services

## Enable & Run

```bash
sudo systemctl daemon-reload
sudo systemctl enable backup-service
sudo systemctl start backup-service
```

# Usage

- Run once (immediate backup)

```bash
backup-service --now
```

- Run as a scheduler (foreground)

```bash
backup-service
```