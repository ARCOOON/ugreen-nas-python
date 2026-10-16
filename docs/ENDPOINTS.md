# UGOS Pro Reverse-Engineered REST Endpoints

This document catalogs key REST endpoints identified from reverse-engineering the UGREEN NAS client application and web frontend bundles.

---

## Authentication & Verification
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/ugreen/v1/verify/check` | Fetch RSA public key for password encryption |
| `POST` | `/ugreen/v1/verify/login` | Authenticate with RSA-encrypted password |
| `GET` | `/ugreen/v1/verify/is_login` | Check if session token is valid |
| `GET` | `/ugreen/v1/verify/heartbeat` | Keepalive heartbeat ping |

## Users & Groups
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/ugreen/v1/user/list` | List all local user accounts |
| `GET` | `/ugreen/v1/user/uid/{uid}` | Get user details by UID |
| `GET` | `/ugreen/v1/user/current/user` | Get currently logged-in user profile |
| `POST` | `/ugreen/v1/user/create` | Create a new user account |
| `POST` | `/ugreen/v1/user/edit` | Update user details, role, and quotas |
| `DELETE` | `/ugreen/v1/user/delete` | Delete user(s) (requires `X-CurPass-Token`) |
| `POST` | `/ugreen/v1/user/online/list` | List active user sessions |
| `POST` | `/ugreen/v1/user/online/stop` | Terminate an active user session |
| `GET` | `/ugreen/v1/group/list` | List local user groups |
| `GET` | `/ugreen/v1/group/info/{gid}` | Get group details by GID |
| `POST` | `/ugreen/v1/group/create` | Create a new user group |
| `POST` | `/ugreen/v1/group/edit` | Edit user group members and description |
| `DELETE` | `/ugreen/v1/group/delete` | Delete a user group |

## Network
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/ugreen/v1/network/iface/list` | List network interfaces and carrier link state |
| `POST` | `/ugreen/v1/network/iface/set` | Configure interface IP, netmask, gateway, DHCP |
| `GET` | `/ugreen/v1/network/general/get` | Get global DNS and default gateway settings |
| `POST` | `/ugreen/v1/network/general/set` | Update global DNS servers |
| `GET` | `/ugreen/v1/network/general/gateway_get`| Get configured gateway routes |
| `POST` | `/ugreen/v1/network/general/gateway_set`| Set primary gateway interface |
| `GET` | `/ugreen/v1/network/bond/status` | Get network bond / teaming status |
| `GET` | `/ugreen/v1/network/bridge/status` | Get network bridge status |

## Storage, Disks, and Volumes
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/ugreen/v2/storage/disk/list` | List physical SATA/NVMe disks, temperature, health |
| `GET` | `/ugreen/v1/storage/disk/smart/info` | S.M.A.R.T. health test attributes |
| `GET` | `/ugreen/v1/storage/pool/list` | List RAID storage pools and sync progress |
| `GET` | `/ugreen/v1/storage/volume/list` | List logical volumes, filesystem, used/free bytes |
| `GET` | `/ugreen/v1/filemgr/getVolumes` | Summarized volume allocation for file manager |
| `POST` | `/ugreen/v1/filemgr/getPathFreeSize` | Get available free space under a path |

## Shares & File Protocols
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/ugreen/v1/filemgr/getShareList` | List shared folders |
| `GET` | `/ugreen/v1/filemgr/shareUserList` | List user permissions for a share |
| `POST` | `/ugreen/v1/filemgr/sharePermission` | Update access permissions for a share |
| `GET` | `/ugreen/v1/file/smb/config` | Get SMB/CIFS configuration |
| `POST` | `/ugreen/v1/file/smb/start` | Start SMB service |
| `POST` | `/ugreen/v1/file/smb/stop` | Stop SMB service |
| `GET` | `/ugreen/v1/file/nfs/config` | Get NFS configuration |
| `POST` | `/ugreen/v1/file/nfs/start` | Start NFS service |
| `POST` | `/ugreen/v1/file/nfs/stop` | Stop NFS service |
| `GET` | `/ugreen/v1/file/ftp/config` | Get FTP service configuration |
| `POST` | `/ugreen/v1/file/ftp/start` | Start FTP service |
| `POST` | `/ugreen/v1/file/ftp/stop` | Stop FTP service |
| `GET` | `/ugreen/v1/file/webdav/config` | Get WebDAV configuration |
| `POST` | `/ugreen/v1/file/webdav/start` | Start WebDAV service |
| `POST` | `/ugreen/v1/file/webdav/stop` | Stop WebDAV service |
| `GET` | `/ugreen/v1/file/rsync/config` | Get Rsync daemon configuration |
| `POST` | `/ugreen/v1/file/rsync/start` | Start Rsync service |
| `POST` | `/ugreen/v1/file/rsync/stop` | Stop Rsync service |

## Power & Hardware
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/ugreen/v1/desktop/reboot` | Reboot the device |
| `POST` | `/ugreen/v1/desktop/poweroff` | Shut down the device |
| `GET` | `/ugreen/v1/hardware/power/config` | Get power recovery, WoL, disk sleep settings |
| `POST` | `/ugreen/v1/hardware/power/start` | Set power configuration |
| `GET` | `/ugreen/v1/hardware/fan/config` | Get fan status and speed profile |
| `POST` | `/ugreen/v1/hardware/fan/setfan` | Set fan mode (1=quiet, 2=standard, 3=full) |
| `GET` | `/ugreen/v1/terminal/get` | Get SSH and Telnet terminal configuration |
| `POST` | `/ugreen/v1/terminal/set` | Configure SSH port, SFTP, and LAN access |
| `GET` | `/ugreen/v1/hardware/buzzer/config` | Get buzzer alert configuration |
| `POST` | `/ugreen/v1/hardware/buzzer/mute` | Mute buzzer alarm |
| `GET` | `/ugreen/v1/hardware/led/config` | Get hardware LED indicator settings |
