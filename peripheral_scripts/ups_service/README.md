# ups-service (Geekworm X1200)

ups-service is a lightweight daemon for monitoring the Geekworm X1200 UPS HAT on Raspberry Pi.
It runs inside its own Python virtual environment, logs events, exposes status for other services (e.g. OLED display), and ensures safe shutdown when the battery is critically low.

# Key Features

- Battery Monitoring
Reads battery charge (%) and voltage (V) via I²C (fuel gauge @ 0x36).

- AC Power Detection
Monitors GPIO pin (default BCM6) to detect if external power supply is present.

- Status File
Publishes current UPS state as JSON in /run/ups-service/status.json for other services.

- Safe Shutdown
If running on battery and charge drops below a threshold (default: 10%) for longer than a debounce period (default: 60s), triggers system shutdown.

- Configurable
All key parameters (I²C bus, GPIO polarity, thresholds, paths) are configurable via environment variables in the systemd unit.

- Structured Service
Same layout and conventions as your other services: src/ code, logging, configs, providers, virtual environment, systemd integration.

# Project Structure

```
ups-service/
├─ src/
│   ├─ main.py              # Entry point
│   ├─ configs.py           # Global settings
│   ├─ ups_logger.py        # Rotating logger
│   ├─ ups_manager.py       # Core manager loop
│   └─ providers/           # Hardware-specific providers
│        ├─ base.py
│        └─ geekworm_x1200.py
├─ pyproject.toml           # Dependencies + venv install
├─ Makefile                 # Minimal CLI (install/start/stop/logs)
└─ README.md
```

# Configuration

| Variable                    | Default                        | Description                                            |
| --------------------------- | ------------------------------ | ------------------------------------------------------ |
| `UPS_I2C_BUS`               | `1`                            | I²C bus number (`/dev/i2c-1`)                          |
| `UPS_I2C_ADDR`              | `0x36`                         | Fuel gauge I²C address                                 |
| `UPS_GPIO_AC_PIN`           | `6`                            | BCM GPIO pin for AC detect                             |
| `UPS_AC_ACTIVE_HIGH`        | `1`                            | Polarity of AC pin (`1=HIGH means AC present`)         |
| `UPS_LOW_BATTERY_PERCENT`   | `10`                           | Shutdown threshold (%)                                 |
| `UPS_LOW_BATT_DEBOUNCE_SEC` | `60`                           | Time battery must stay below threshold before shutdown |
| `UPS_STATE_DIR`             | `/run/ups-service`             | Directory for state files                              |
| `UPS_STATUS_PATH`           | `/run/ups-service/status.json` | Path to status JSON                                    |
| `UPS_LOG_PATH`              | `/var/log/ups-service.log`     | Log file path                                          |
| `UPS_DRY_RUN`               | `0`                            | If `1`, disables shutdown (for testing)                |

# Status JSON Example

```json
{
  "ts": 1725001234,
  "ac_present": true,
  "charging": true,
  "soc_percent": 84.5,
  "voltage_v": 3.925
}
```