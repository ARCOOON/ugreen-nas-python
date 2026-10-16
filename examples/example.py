#!/usr/bin/env python3
"""Example: Connect to UGREEN NAS and manage resources using the Python OOP SDK."""

import os
import sys

# Ensure local SDK package is in path when running from examples/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ugreen_nas import UgreenNasClient

# Read configuration from environment
UGLINK_ID = os.getenv("UGREEN_NAS_UGLINK", "https://ug.link/your-nas-alias")
BASE_URL = os.getenv("UGREEN_NAS_URL")  # e.g. "https://192.168.1.100"
USERNAME = os.getenv("UGREEN_NAS_USER", "admin")
PASSWORD = os.getenv("UGREEN_NAS_PASS", "your-password")


def main():
    print("Initializing UGREEN NAS client...")
    if BASE_URL:
        client = UgreenNasClient(base_url=BASE_URL)
    else:
        client = UgreenNasClient(uglink_id=UGLINK_ID)

    print(f"Connecting to {client.base_url}...")
    client.login(USERNAME, PASSWORD)
    print("Authentication successful!")

    # 1. Inspect Hardware & System
    sysinfo = client.get_system_info()
    print(f"Device: {sysinfo.get('model', 'UGREEN NAS')} (OS: {sysinfo.get('version')})")

    # 2. Users & Sessions
    print("\n[Users]")
    for user in client.users.all():
        print(f" - {user.username} (UID: {user.uid}, Admin: {user.is_admin})")

    # 3. Network Interfaces
    print("\n[Network Interfaces]")
    for iface in client.network.interfaces.all():
        print(f" - {iface.name}: {iface.ip} (Connected: {iface.is_connected})")

    # 4. Storage & Disks
    print("\n[Physical Drives]")
    for disk in client.storage.disks.all():
        print(
            f" - {disk.name}: {disk.model} ({disk.size_tb} TB), "
            f"Temp: {disk.temperature}°C, Healthy: {disk.is_healthy}"
        )

    print("\n[Volumes]")
    for vol in client.storage.volumes.all():
        print(f" - {vol.name}: {vol.used_gb} GB / {vol.total_tb} TB ({vol.usage_percent}%)")

    # 5. Shared Folders
    print("\n[Shared Folders]")
    for share in client.shares.all():
        print(f" - {share.name} ({share.path})")

    # 6. Fan & Power
    fan = client.power.fan
    print(f"\nFan Mode: {fan.mode.name}")


if __name__ == "__main__":
    main()
