#!/usr/bin/env python3
from .wifi_lan_manager import LanWifiPolicy, log

def main():
    try:
        policy = LanWifiPolicy()
        policy.apply()
        log.info("[LanWifiPolicy] Policy applied successfully.")
    except Exception as e:
        log.error(f"[LanWifiPolicy] Failed to apply LAN/Wi-Fi policy: {e}", exc_info=True)

if __name__ == '__main__':
    main()
