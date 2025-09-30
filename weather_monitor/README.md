# Weather Monitor

`weather-monitor` is a Python service that periodically fetches weather data from external APIs and makes it available to other local services (e.g., OLED dashboards).

## Key Features

-   **Provider Fallback:** Uses multiple providers (OpenWeatherMap, WeatherAPI.com) and falls back to the next one if a request fails.
-   **Flexible Location Sources:** Can read coordinates from another service via a UNIX socket or use static values from its configuration as a fallback.
-   **Multiple Outputs:**
    -   `ConsoleOutput`: Logs human-readable weather data to the console.
    -   `SocketOutput`: Serves the latest weather data as JSON over a UNIX socket.
    -   `FileOutput`: Periodically saves the weather data to a JSON file.
-   **Unified Data Model:** Normalizes data from all providers into a single, consistent `WeatherData` format.
-   **Log Rotation:** Manages log files automatically to prevent disk space issues.

---

## Configuration

The service is configured via environment variables.

| Variable                 | Description                                                  |
| ------------------------ | ------------------------------------------------------------ |
| `OPENWEATHERMAP_API_KEY` | Your API key for OpenWeatherMap.                             |
| `WEATHERAPI_API_KEY`     | Your API key for WeatherAPI.com.                             |
| `LOCATION_SERVICE_SOCKET`| Path to the UNIX socket for the location service.            |
| `WEATHER_SERVICE_SOCKET` | Path for the UNIX socket where this service provides weather JSON. |
| `ON_DEMAND_WEATHER_SOCKET`| Path for the UNIX socket used for on-demand weather requests.  |
| `WEATHER_JSON_FILE_PATH` | Path where the `latest.json` file is saved.                  |
| `LOG_FILE_PATH`          | Path to the log file.                                        |
| `DEFAULT_LATITUDE`       | Fallback latitude if the location service is unavailable.    |
| `DEFAULT_LONGITUDE`      | Fallback longitude if the location service is unavailable.   |
| `INTERVAL_SECONDS`       | Refresh interval for fetching weather data (in seconds).     |
| `JSON_INTERVAL_SECONDS`  | Interval for saving data to the JSON file.                   |

---

## How to Run

You can run this service using Docker (recommended) or natively on your system.

### Running with Docker (Recommended)

This method handles all dependencies and ensures a consistent environment.

**Prerequisites:**
* `Docker`
* `Docker Compose`

**Instructions:**

**Step 1: Clone the repository**
```bash
git clone [your-repo-url]
cd weather-monitor
```

**Step 2: Prepare Host Directories (First Time Setup)**
Before the first launch, you must create the directories on the host machine that Docker will use for persistent storage. This ensures the application has the necessary permissions to write files.

```bash
# Create directory for the JSON output file and grant permissions
sudo mkdir -p /run/monitors/weather
sudo chmod 777 /run/monitors/weather

# Create directory for logs in your project folder and grant permissions
mkdir -p ./logs
sudo chmod 777 ./logs
```

**Step 3: Set up the environment**
Copy the production environment template and add your secret API keys.
```bash
cp .env.prod.template .env.prod
nano .env.prod
```

**Step 4: Build and run the container**
This command will build the Docker image and start the service in the background.
```bash
docker-compose up --build -d
```

**Step 5: Check the logs**
To see the application output or troubleshoot issues, run:
```bash
docker-compose logs -f
```

**Step 6: Stop the application**
To stop and remove the container, run:
```bash
docker-compose down
```

### Running Natively (Legacy)

This method requires installing Python and dependencies directly on your system.

**Prerequisites:**
* Python >= 3.10

**Instructions:**

**Step 1: Installation**
Create a virtual environment and install the project dependencies.
```bash
cd /path/to/weather-monitor
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

**Step 2: Configuration**
Export the required environment variables in your shell before running the application.
```bash
export OPENWEATHERMAP_API_KEY="your_key_here"
export WEATHERAPI_API_KEY="your_key_here"
# Export other variables if you need to override the defaults
# export LOG_FILE_PATH="/path/to/your/logs/weather.log"
```

**Step 3: Run**
Execute the installed script.
```bash
weather-monitor
```
To run it as a persistent background service, you will need to configure a process manager like `systemd`.