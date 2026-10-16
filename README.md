# UGREEN NAS Python SDK

[![Python CI](https://github.com/ARCOOON/ugreen-nas-python/actions/workflows/ci.yml/badge.svg)](https://github.com/ARCOOON/ugreen-nas-python/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Object-Oriented Management SDK for **UGREEN NAS** devices running **UGOS Pro / UGOS** (DXP series: DXP2800, DXP4800, DXP6800, DXP8800).

Provides first-class Python domain models (`User`, `Group`, `NetworkInterface`, `Disk`, `Volume`, `SharedFolder`, etc.) with rich properties and behavior methods.

---

## Features

- **Direct & Remote (UGREENlink) Access**: Connect via local IP (`https://192.168.1.x`) or by passing your UGREENlink ID (e.g. `my-nas-alias` or `https://ug.link/my-nas-alias`). The SDK automatically resolves relay domains via `api.ugnas.com`.
- **Zero-Config RSA Authentication**: Handshakes with the NAS RSA public key and encrypts passwords using PKCS#1 v1.5.
- **Rich Domain Models**:
  - `user.edit(...)`, `user.delete(admin_password=...)`, `session.terminate()`
  - `group.edit(...)`, `group.delete()`
  - `iface.set_dhcp()`, `iface.set_static_ip(...)`
  - `disk.get_smart_info()`, `disk.temperature`, `disk.is_healthy`
  - `volume.get_path_free_size(...)`, `volume.used_gb`, `volume.usage_percent`
  - `share.get_users()`, `share.set_permissions(...)`
  - `services.smb.enable()`, `services.nfs.disable()`, `services.ssh.enable(...)`
  - `power.fan.set_mode(FanMode.STANDARD)`, `power.settings.update(...)`, `power.reboot()`, `power.poweroff()`

---

## Supported Functionality

| Category | Features |
|---|---|
| **Users & Groups** | Local users, roles (`admin`, `users`), directory quotas, user group memberships, active session termination |
| **Network & IP** | Interface enumeration, link carrier status, DHCP vs Static IPv4, MTU, global DNS servers, gateway routing |
| **Storage & Disks** | SATA HDD & NVMe SSD status, slot bay mapping, temperature, S.M.A.R.T. health queries, RAID storage pools, volume allocation and path free size |
| **Shared Folders** | Shared folder creation, mount points, volume mapping, user/group read/write permissions |
| **File Services** | Service management for SMB/CIFS, NFS, FTP, WebDAV, Rsync, and SSH/SFTP terminal |
| **Power & Hardware** | Shutdown, reboot, Wake-on-LAN, AC power recovery, disk standby sleep timers, fan profiles (Quiet/Standard/Full), and buzzer control |

---

## Installation

### From Pre-Built Wheel (`.whl`)
Download `ugreen_nas-1.1.0-py3-none-any.whl` from GitHub Actions artifacts or Releases:
```bash
pip install ugreen_nas-1.1.0-py3-none-any.whl
```

### From Source / Build Wheel Locally
```bash
# Editable install
pip install -e .

# Or build a .whl wheel into dist/
pip install build
python -m build
pip install dist/*.whl
```

Requires `cryptography>=3.4.0` (or `pycryptodome`).

---

## Quickstart & OOP Usage

```python
from ugreen_nas import UgreenNasClient, FanMode

# Connect via UGREENlink or local URL
client = UgreenNasClient(uglink_id="https://ug.link/my-nas-alias")
# or: client = UgreenNasClient(base_url="https://192.168.1.100")

# Authenticate
client.login("admin", "my-password")

# 1. Users & Active Sessions
for user in client.users.all():
    print(f"User: {user.username} (Admin: {user.is_admin}, Quota: {user.dir_quota_bytes})")
    # user.edit(description="Updated description")
    # user.delete(admin_password="current-admin-password")

for session in client.users.sessions():
    print(f"Session {session.session_id} from {session.client_ip} (Current: {session.is_current_connection})")
    # session.terminate()

# 2. Network Management
for iface in client.network.interfaces.all():
    print(f"Interface {iface.name}: IP={iface.ip}, MAC={iface.mac_address}, Link={iface.is_connected}")
    # iface.set_static_ip(ip="192.168.1.50", subnet_mask="255.255.255.0", gateway="192.168.1.1")
    # iface.set_dhcp()

gen_net = client.network.get_general_settings()
print(f"DNS Servers: {gen_net.dns_servers}, Gateway: {gen_net.default_gateway_ip}")
# gen_net.set_dns(["1.1.1.1", "8.8.8.8"])

# 3. Storage, Disks, and Volumes
for disk in client.storage.disks.all():
    print(f"Disk {disk.name}: {disk.model} ({disk.size_tb} TB) Temp: {disk.temperature}°C Healthy: {disk.is_healthy}")
    smart = disk.get_smart_info()

for pool in client.storage.pools.all():
    print(f"Storage Pool {pool.name}: RAID={pool.raid_level}, Capacity={pool.total_tb} TB")

for vol in client.storage.volumes.all():
    print(f"Volume {vol.name}: {vol.used_gb} GB / {vol.total_tb} TB ({vol.usage_percent}%)")
    free_bytes = vol.get_path_free_size("downloads")

# 4. Shares & File Services
for share in client.shares.all():
    print(f"Share {share.name} on {share.path} (Mounted: {share.is_mounted})")
    users = share.get_users()

# Manage file sharing services
if not client.services.smb.is_enabled:
    client.services.smb.enable()

client.services.nfs.enable()
client.services.ssh.enable(port=22, lan_only=True)

# 5. Power & Hardware Controls
fan = client.power.fan
print(f"Fan Mode: {fan.mode.name}")
fan.set_mode(FanMode.STANDARD)

pwr = client.power.settings
print(f"Wake-on-LAN: {pwr.wake_on_lan}, HDD Sleep: {pwr.hdd_sleep_minutes}m")
pwr.update(wake_on_lan=True, hdd_sleep_minutes=15)

# client.power.reboot()
# client.power.poweroff()
```

---

## Documentation

- [Architecture & Protocol Specification](docs/ARCHITECTURE.md) - Deep dive into relay lookup, RSA SPKI handshake, and session tokens.
- [API Reference](docs/API_REFERENCE.md) - Detailed reference for all Python classes, methods, and properties.
- [Reverse-Engineered Endpoints](docs/ENDPOINTS.md) - Catalog of 200+ UGOS Pro REST endpoints.
- [Runnable Example](examples/example.py) - Example script with environment configuration.

---

## Disclaimer

This project is an independent open-source project and is not affiliated with, endorsed by, or associated with UGREEN (Shenzhen Ugreen Technology Co., Ltd.). UGOS and UGREEN are trademarks of Shenzhen Ugreen Technology Co., Ltd.

## License

[MIT](LICENSE)
