# UGREEN NAS Python SDK - API Reference

Complete class, method, and property reference for the Python SDK (`ugreen_nas`).

---

## 1. `UgreenNasClient`

Core connection coordinator and authentication manager.

### Constructor
```python
UgreenNasClient(
    base_url: str | None = None,
    uglink_id: str | None = None,
    timeout: float = 30.0,
)
```

### Client Properties
| Property | Type | Description |
|---|---|---|
| `users` | `UserManager` | User accounts, quotas, and sessions manager |
| `groups` | `GroupManager` | Local group management |
| `network` | `NetworkManager` | Interfaces, IP addresses, DNS, and gateway manager |
| `storage` | `StorageManager` | Physical drives, RAID pools, and volumes manager |
| `shares` | `ShareManager` | Shared folder paths, permissions, and protocols |
| `services` | `ServicesManager` | File sharing daemons (SMB, NFS, FTP, WebDAV, Rsync, SSH) |
| `power` | `PowerManager` | Power states, reboot, shutdown, fan control, and sleep timers |

### Client Methods
- `login(username: str, password: str, keepalive: bool = True) -> dict`: Authenticates with RSA encryption and acquires session tokens.
- `is_logged_in() -> bool`: Returns `True` if session is active.
- `heartbeat() -> dict`: Keeps the session alive.
- `get_system_info() -> dict`: Hardware model, CPU, serial, and OS version.
- `get_system_stats() -> dict`: Real-time CPU, RAM, network, and disk metrics.

---

## 2. Users & Sessions (`client.users`)

### `UserManager`
- `all(reverse: bool = False) -> list[User]`: List all local users.
- `get(uid: int) -> User | None`: Look up user by UID.
- `get_by_name(username: str) -> User | None`: Look up user by username.
- `current() -> User`: Profile of logged-in user.
- `create(username: str, password: str, role: str = "users", ...) -> User`: Create a new user.
- `edit(uid: int, ...) -> dict`: Update user role, email, phone, or quota.
- `delete(uids: int | list[int], admin_password: str) -> bool`: Delete users (requires admin password).
- `sessions(page_num: int = 1, page_size: int = 50) -> list[UserSession]`: List active login sessions.
- `terminate_session(session_id: int | str) -> bool`: Disconnect active session.

### `User` Model
| Property / Method | Returns | Description |
|---|---|---|
| `username` | `str` | Account username |
| `uid` | `int` | User identifier |
| `role` | `str` | `"admin"` or `"users"` |
| `is_admin` | `bool` | True if user has administrative rights |
| `email` | `str` | Email address |
| `phone` | `str` | Phone number |
| `dir_quota_bytes` | `int` | Directory disk quota in bytes |
| `groups` | `list[dict]` | Group memberships |
| `edit(...)` | `User` | Updates user details and refreshes self |
| `delete(admin_password)` | `bool` | Deletes this user |

### `UserSession` Model
| Property / Method | Returns | Description |
|---|---|---|
| `session_id` | `int` | Unique session ID |
| `username` | `str` | Logged-in user |
| `client_ip` | `str` | Remote IP address |
| `host` | `str` | Host / domain |
| `is_current_connection` | `bool` | True if this is the active SDK connection |
| `connection_duration_seconds` | `int` | Duration connected in seconds |
| `terminate()` | `bool` | Disconnect this session |

---

## 3. Network (`client.network`)

### `NetworkManager`
- `interfaces.all() -> list[NetworkInterface]`: All network adapters.
- `interfaces.get(name: str) -> NetworkInterface | None`: Get adapter by name (e.g. `"eth0"`).
- `get_general_settings() -> GeneralNetworkSettings`: DNS servers, default gateway.
- `set_general_settings(dns: list[str] = None, ...) -> dict`: Configure global DNS.
- `get_gateways() -> dict`: Current IPv4/IPv6 gateways.
- `set_default_gateway(iface_name: str, gateway_ip: str) -> dict`: Set primary network gateway.

### `NetworkInterface` Model
| Property / Method | Returns | Description |
|---|---|---|
| `name` | `str` | Adapter name (`eth0`, `eth1`) |
| `is_connected` | `bool` | Physical link carrier status |
| `mac_address` | `str` | Hardware MAC address |
| `ip` | `str` | Current IPv4 address |
| `netmask` | `str` | Subnet mask |
| `gateway` | `str` | Interface default gateway |
| `dns` | `list[str]` | Per-interface DNS servers |
| `is_dhcp` | `bool` | True if DHCP client is enabled |
| `mtu` | `int` | MTU size (default 1500) |
| `set_dhcp(mtu: int = 1500)` | `NetworkInterface` | Switches interface to automatic DHCP |
| `set_static_ip(ip, subnet_mask, ...)` | `NetworkInterface` | Assigns static IP configuration |

---

## 4. Storage & Disks (`client.storage`)

### `StorageManager`
- `disks.all() -> list[Disk]`: Physical SATA HDDs and NVMe SSDs.
- `disks.get(slot_or_name: str) -> Disk | None`: Get drive by device name (`"sda"`) or slot (`"ata1"`).
- `pools.all() -> list[StoragePool]`: RAID storage pools.
- `volumes.all() -> list[Volume]`: Logical filesystems.
- `get_path_free_size(path: str) -> int`: Free space in bytes under a path.

### `Disk` Model
| Property / Method | Returns | Description |
|---|---|---|
| `name` | `str` | Dev name (`sda`, `nvme0n1`) |
| `model` | `str` | Drive manufacturer model |
| `serial` | `str` | Hardware serial number |
| `slot` | `str` | Bay slot (`ata1`, `nvme1`) |
| `size_tb` / `size_gb` | `float` | Storage capacity |
| `temperature` | `int | None` | Temperature in Celsius |
| `is_healthy` | `bool` | True if drive is healthy |
| `get_smart_info()` | `dict` | Fetch latest S.M.A.R.T. health test attributes |

### `Volume` Model
| Property / Method | Returns | Description |
|---|---|---|
| `name` | `str` | Volume name (`dm-0`, `volume1`) |
| `filesystem` | `str` | Filesystem (`btrfs`, `ext4`) |
| `total_tb` / `used_gb` | `float` | Volume space allocation |
| `usage_percent` | `float` | Percentage of space consumed |
| `get_path_free_size(subpath: str = "")` | `int` | Remaining free space under volume path |

---

## 5. Shares & Protocols (`client.shares` / `client.services`)

### `ShareManager`
- `all() -> list[SharedFolder]`: List all shared network folders.
- `get(id_or_name: int | str) -> SharedFolder | None`: Lookup share by name or ID.
- `get_share_users(share_id: int) -> list[dict]`: Access permission rules.
- `set_share_permissions(share_id: int, permissions: list[dict]) -> dict`: Apply read/write permissions.

### `SharedFolder` Model
| Property / Method | Returns | Description |
|---|---|---|
| `id` | `int` | Share identifier |
| `name` | `str` | Folder share name |
| `path` | `str` | Absolute path on volume (`/volume1/downloads`) |
| `is_mounted` | `bool` | Volume mount status |
| `get_users()` | `list[dict]` | Access rights for users and groups |
| `set_permissions(rules)` | `dict` | Update user/group permissions |

### `ServicesManager` (`client.services`)
- `client.services.smb`: SMB/CIFS service (`is_enabled`, `workgroup`, `enable()`, `disable()`).
- `client.services.nfs`: NFS server (`is_enabled`, `enable()`, `disable()`).
- `client.services.ftp`: FTP daemon (`enable()`, `disable()`).
- `client.services.webdav`: WebDAV server (`enable()`, `disable()`).
- `client.services.rsync`: Rsync daemon (`enable()`, `disable()`).
- `client.services.ssh`: SSH terminal (`is_enabled`, `port`, `is_lan_only`, `enable()`, `disable()`).

---

## 6. Power & Hardware (`client.power`)

### `PowerManager`
- `fan`: `FanControl` profile manager.
- `settings`: `PowerSettings` model.
- `reboot() -> bool`: Device reboot.
- `poweroff() -> bool`: Device shutdown.
- `mute_buzzer() -> dict`: Mute alert tone.

### `FanControl` Model
- `mode`: Current speed (`FanMode.QUIET`, `FanMode.STANDARD`, `FanMode.FULL_SPEED`).
- `set_mode(mode: FanMode | int) -> bool`: Update fan speed.

### `PowerSettings` Model
- `wake_on_lan`: Wake-on-LAN enabled.
- `power_boot_on_ac`: Automatic boot after power restoration.
- `hdd_sleep_minutes`: Drive standby timer (0 = never sleep).
- `update(wake_on_lan=..., hdd_sleep_minutes=...) -> PowerSettings`: Save changes.
