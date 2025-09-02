# network-policy

`network-policy` is a lightweight service that automatically switches Wi-Fi based on LAN state on Raspberry Pi (or any Linux host).

When the wired interface is UP, the policy blocks Wi-Fi; when the wired interface is DOWN, the policy can optionally unblock Wi-Fi (configurable). 


# Key Features

- LAN-aware Wi-Fi control — Detects whether the configured LAN interface is up/down and applies the corresponding Wi-Fi policy. 

- Auto-unblock option — If enabled, Wi-Fi is automatically unblocked when LAN goes down. 

- Structured logging — Uses the shared logger and writes to a project log file under your peripherals root. 

- Simple CLI entrypoint — Run the policy via the network-policy-apply command.

# Project Structure

```bash
network-policy/
├─ wifi_lan_managers/
│  ├─ configs.py        # env-config: PERIPHERALS_ROOT, LOG path, LAN_INTERFACE, AUTO_UNBLOCK
│  ├─ main.py           # logger setup + policy runner
│  └─ policy.py         # LanWifiPolicy (core logic)
├─ pyproject.toml       # package metadata + CLI script
└─ README.md
```

# Installation

Requires Python ≥ 3.9 and your internal common-utils package (for logging and system helpers).

```bash
pip install .
```

# Configuration

| Variable                     | Default                            | Description                                                                          |
| ---------------------------- | ---------------------------------- | ------------------------------------------------------------------------------------ |
| `PERIPHERALS_ROOT`           | `/home/reekroo/peripheral_scripts` | Base folder; logs are under `${PERIPHERALS_ROOT}/logs/`.                             |
| `LAN_INTERFACE`              | `eth0`                             | The wired interface name to monitor.                                                 |
| `AUTO_UNBLOCK_WHEN_LAN_DOWN` | `0` (disabled)                     | If `"1"`, `"true"`, or `"True"`, Wi-Fi is automatically unblocked when LAN is down.  |

# Systemd Integration

Take the systemd file from here: https://github.com/reekroo/media-server/tree/main/deployment/systemd_services

## Enable & Run

```bash
sudo systemctl daemon-reload
sudo systemctl enable network-policy.service
sudo systemctl start network-policy.service
sudo systemctl status network-policy.service
```

## Logging

```bash
${PERIPHERALS_ROOT}/logs/network_policy.log
```