# backup-service

`backup-service` creates timestamped ZIP archives of your configured directories and uploads them to Google Drive on a schedule.

## Key Features

- Zip archiving of one or more source directories.
- Google Drive upload using OAuth2 (token is cached locally).
- Flexible scheduling (weekly/daily).
- Rotating logs via `concurrent-log-handler`.
- Immediate backup execution via a CLI flag.

---

## Deployment with Docker (Recommended)

This method encapsulates all dependencies and provides a clear process for the one-time authentication required by Google APIs.

### Prerequisites
* `Docker`
* `Docker Compose`

### One-Time Setup & Authentication

This process authenticates the service with your Google Account and creates a persistent `token.json` file. **You only need to do this once.**

**1. Prepare Google API Credentials:**
   - Follow **Step 1, 2, and 3** from the "Google Account Setup" section in the legacy instructions below to get your `credentials.json` file and your `GOOGLE_DRIVE_FOLDER_ID`.

**2. Prepare Local Directories:**
   Create the necessary folders in your project directory on the host machine.
   ```bash
   # Create folders for logs, temporary archives, and config files
   mkdir -p ./logs ./temp ./config
   ```

**3. Place `credentials.json`:**
   Move the `credentials.json` file you downloaded from Google into the newly created `./config` directory.

**4. Configure `.env.prod`:**
   Copy the template and edit the file to add your `GOOGLE_DRIVE_FOLDER_ID`.
   ```bash
   cp .env.prod.template .env.prod
   nano .env.prod
   ```

**5. Run the Interactive Authentication:**
   Execute the following command. This will run the container in the foreground and attach your terminal, allowing you to complete the Google authentication flow.
   ```bash
   docker-compose run --rm backup-service
   ```
   - The console will display a URL. Copy it and paste it into your web browser.
   - Log in to your Google account and grant the requested permissions.
   - Google will provide you with an authorization code. Copy it.
   - Paste the code back into your terminal and press Enter.
   - If successful, you will see a message "Token saved to file," and a `token.json` will appear in your `./config` directory. The container will then exit.

### Normal Scheduled Operation

After the one-time setup is complete, you can start the service in its normal, detached mode.

**1. Start the service:**
   ```bash
   docker-compose up -d --build
   ```
   The service will now run in the background and perform backups according to the schedule defined in `.env.prod`.

**2. Check the logs:**
   ```bash
   docker-compose logs -f
   ```

**3. Stop the service:**
   ```bash
   docker-compose down
   ```

**4. Run an immediate backup:**
   To trigger a one-time backup without waiting for the schedule, use the `--now` flag.
   ```bash
   docker-compose run --rm backup-service --now
   ```

---

## Legacy / Native Setup

### Google Account Setup

To work, the service needs permission to access your Google Drive. This is a one-time setup.

**1. Step 1: Obtaining `credentials.json`**

This file is the key that allows your application to request access to the Google API.

* Go to the [Google Cloud Console](https://console.cloud.google.com/) and create a new project.
* In the navigation menu (☰), open "APIs & Services" -> "Library". Find the "Google Drive API" and enable it (click the Enable button).
* Return to "APIs & Services" and go to the "Credentials" section.
* Click "+ CREATE CREDENTIALS" -> "OAuth client ID".
* For "Application type," select "Desktop app" and give it a name (e.g., "Backup Service").
* After creation, click "DOWNLOAD JSON". Rename the downloaded file to `credentials.json` and place it in the root folder of your project.

**2. Step 2: Add a test user**

* Go to the [Google Cloud Console](https://console.cloud.google.com/) 
* In the navigation menu (☰), open "APIs & Services" -> "OAuth consent screen"
* Click "+ Add users" in the "Audience" section

**3. Step 3: Obtaining `GOOGLE_DRIVE_FOLDER_ID`**

This is the ID of the folder on your Google Drive where the archives will be uploaded.

* Create or select a folder on [Google Drive](https://drive.google.com/).
* Open it. The ID will be at the end of the URL in your browser's address bar.
Example: https://drive.google.com/drive/folders/1a2b3c4d5e6f7g8h9i0j
Your ID here is: 1a2b3c4d5e6f7g8h9i0j.

### Installation

Requires Python ≥ 3.9. Uses requests and concurrent-log-handler (declared in pyproject.toml).

Install inside your virtual environment or system

```Bash
cd ~/backup_service
python3 -m venv .venv_backup_service
source .venv_backup_service/bin/activate
pip install -e .

#copy client secret to the root service folder
#run main script manually to activate google account

python -m src.main

#authenticate as an real user
#provided generated code to the console window
#your pesonal token is generated

deactivate

#for immidiate run the solution use the command from console

sudo /home/reekroo/backup_service/.venv_backup_service/bin/python -m src.main --now
```

### Configuration

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

### Systemd Integration

Take the systemd file from here: https://github.com/reekroo/media-server/tree/main/deployment/systemd_services

#### Enable & Run

```bash
sudo systemctl daemon-reload
sudo systemctl enable backup-service
sudo systemctl start backup-service
```