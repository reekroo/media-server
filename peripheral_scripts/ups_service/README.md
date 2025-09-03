# ups-service

`ups-service` is a Python daemon that monitors a Geekworm X1200 UPS module on Raspberry Pi via I²C and GPIO.
It tracks battery voltage and state of charge (SoC), detects AC adapter presence, applies shutdown policies on low battery, and writes real-time status to JSON for other services to consume.

# Key Features

- Geekworm X1200 integration — Reads SoC (%) and voltage (V) from the UPS chip via I²C, and AC presence via GPIO. 

- Graceful shutdown policy — Configurable thresholds (low SoC %, critical voltage V, debounce period) trigger a safe system shutdown when battery is critically low. 

- Status export — Writes current readings to JSON (status.json) for dashboards, OLED display services, or external consumers. 

- Display SoC smoothing — Includes a display-specific SoC calculator that prevents fluctuations when on battery, for stable UI output. 

- Structured logging — Logs to ${PERIPHERALS_ROOT}/logs/ups.log for troubleshooting. 

- CLI entrypoint — Run with ups-service (defined in pyproject.toml).

```bash
ups-service/
├─ src/
│  ├─ configs.py                  # Environment-based config: paths, pins, thresholds
│  ├─ main.py                     # Service entrypoint (logger + UpsService)
│  ├─ ups_service.py              # Main service loop
│  ├─ shutdown_policy.py          # Low-battery shutdown logic
│  ├─ status_writer.py            # Writes JSON status
│  ├─ display_soc_calculator.py   # Smoothed display SoC
│  └─ providers/
│     ├─ geekworm_x1200.py        # UPS hardware integration
│     └─ ups_reading_interface.py # Abstract provider + reading dataclass
├─ pyproject.toml                 # package metadata + CLI script
└─ README.md
```

# Installation

Requires Python ≥ 3.10 and hardware access to I²C + GPIO on Raspberry Pi.

Install inside your virtual environment or system

```bash
pip install .
```

Ensure system packages are enabled:

1. I²C bus enabled (`raspi-config` or `config.txt`)
2. Python can access `/dev/i2c-*` and `GPIO`

# Configuration

| Variable                    | Default Path / Value                                  | Description                               |
| --------------------------- | ----------------------------------------------------- | ----------------------------------------- |
| `PERIPHERALS_ROOT`          | `/home/reekroo/peripheral_scripts`                    | Root folder for logs                      |
| `PERIPHERALS_RUN_ROOT`      | `/run/peripherals`                                    | Root for runtime state files              |
| `UPS_STATUS_PATH`           | `${RUN_ROOT}/ups/status.json`                         | JSON output file                          |
| `UPS_LOG_FILE`              | `${PERIPHERALS_ROOT}/logs/ups.log`                    | Log file                                  |
| `UPS_I2C_BUS`               | `1`                                                   | I²C bus index                             |
| `UPS_I2C_ADDR`              | `0x36`                                                | I²C device address                        |
| `UPS_GPIO_AC_PIN`           | `6`                                                   | GPIO pin for AC presence                  |
| `UPS_AC_ACTIVE_HIGH`        | `1`                                                   | `1` = HIGH = AC present                   |
| `UPS_POLL_INTERVAL_SEC`     | `5`                                                   | Polling interval in seconds               |
| `UPS_LOW_BATTERY_PERCENT`   | `10`                                                  | Shutdown threshold for SoC (%)            |
| `UPS_LOW_BATT_DEBOUNCE_SEC` | `60`                                                  | Debounce before shutdown (s)              |
| `UPS_CRITICAL_VOLTAGE_V`    | `3.1`                                                 | Shutdown threshold (V)                    |
| `UPS_VOLTAGE_MIN`           | `3.0`                                                 | Min voltage for SoC calc                  |
| `UPS_VOLTAGE_MAX`           | `4.2`                                                 | Max voltage for SoC calc                  |
| `UPS_DRY_RUN`               | `0`                                                   | If `1`, log shutdown instead of executing |
| `UPS_SHUTDOWN_CMD`          | `/sbin/shutdown -h now 'UPS: battery critically low'` | Command executed on critical shutdown     |

# Systemd Integration

Take the systemd file from here: https://github.com/reekroo/media-server/tree/main/deployment/systemd_services

## Enable & Run

```bash
sudo systemctl daemon-reload
sudo systemctl enable ups-service
sudo systemctl start ups-service
sudo systemctl status ups-service
```

# Status Output

```json
{
  "ts": 1756646497.145,
  "ac_present": false,
  "voltage_v": 3.897,
  "soc_chip_percent": 85.32,
  "soc_display_percent": 84.91
}
```

# Troubleshooting

- Check logs:

```bash
tail -f /home/reekroo/peripheral_scripts/logs/ups.log
```

- Check JSON output:

```bash
cat /run/peripherals/ups/status.json
```