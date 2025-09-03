# bluetooth-policy

`bluetooth-policy` is a lightweight service that forcibly disables Bluetooth at boot on Raspberry Pi.

It runs as a one-shot systemd unit, sequentially trying multiple blocking strategies (`rfkill → bluetoothctl → hciconfig`) and logs all results for troubleshooting.

# Key Features

- Multi-strategy blocking

Tries methods in order:
1. rfkill block bluetooth
2. bluetoothctl power off
3. hciconfig hciX down

- The first successful method is considered sufficient.

Configurable method & device
Environment variables let you set the preferred method (rfkill, bluetoothctl, hciconfig) and target device (hci0 by default).

- Structured logging

Logs are written to ${PERIPHERALS_ROOT}/logs/bluetooth_policy.log (default: /home/reekroo/peripheral_scripts/logs/bluetooth_policy.log).
Uses the shared logger from common-utils.

- Simple CLI entrypoint

Provides a command-line tool:

```bash
bluetooth-policy-apply
```

# Project Structure

```bash
bluetooth-policy/
├─ bluetooth_managers/
│  ├─ configs.py        # log path, BT_BLOCK_METHOD, BT_DEVICE
│  ├─ main.py           # setup_logger + policy runner
│  ├─ policy.py         # orchestrator with fallback logic
│  └─ strategies.py     # rfkill / bluetoothctl / hciconfig implementations
├─ pyproject.toml       # package metadata + CLI script
└─ README.md
```

# Installation

Requires Python ≥ 3.9 and system tools: `rfkill`, `bluetoothctl`, `hciconfig`.

Install inside your virtual environment or system

```bash
pip install .
```

# Configuration

| Variable           | Default                            | Description                                                          |
| ------------------ | ---------------------------------- | -------------------------------------------------------------------- |
| `PERIPHERALS_ROOT` | `/home/reekroo/peripheral_scripts` | Base path for logs (`${PERIPHERALS_ROOT}/logs/bluetooth_policy.log`) |
| `BT_BLOCK_METHOD`  | `rfkill`                           | Primary method: `rfkill` \| `bluetoothctl` \| `hciconfig`            |
| `BT_DEVICE`        | `hci0`                             | Bluetooth adapter name (used by `hciconfig`)                         |

# Systemd Integration

Take the systemd file from here: https://github.com/reekroo/media-server/tree/main/deployment/systemd_services

## Enable & Run

```bash
sudo systemctl daemon-reload
sudo systemctl enable bluetooth-manager.service
sudo systemctl start bluetooth-manager.service
sudo systemctl status bluetooth-manager.service
```

## Logging

```bash
${PERIPHERALS_ROOT}/logs/bluetooth_policy.log
```