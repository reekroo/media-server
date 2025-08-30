#!/usr/bin/env python3
from .bluetooth_manager import BluetoothPolicy, log

def main():
    try:
        policy = BluetoothPolicy()
        policy.apply()
        log.info("[BluetoothPolicy] Policy applied successfully.")
    except Exception as e:
        log.error(f"[BluetoothPolicy] Failed to apply policy: {e}", exc_info=True)

if __name__ == "__main__":
    main()
