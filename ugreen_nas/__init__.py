"""UGREEN NAS Management SDK for Python."""

from .client import UgreenNasClient
from .enums import FanMode, RaidLevel, SshStatus, UserRole
from .exceptions import (
    UgreenNasApiError,
    UgreenNasAuthError,
    UgreenNasError,
    UgreenNasHttpError,
)
from .managers import (
    DiskManager,
    GroupManager,
    NetworkInterfaceManager,
    NetworkManager,
    PowerManager,
    ServicesManager,
    ShareManager,
    StorageManager,
    StoragePoolManager,
    UserManager,
    VolumeManager,
)
from .models import (
    Disk,
    FanControl,
    FileService,
    FtpService,
    GeneralNetworkSettings,
    Group,
    NasResource,
    NetworkInterface,
    NfsService,
    PowerSettings,
    RsyncService,
    SharedFolder,
    SmbService,
    SshTerminal,
    StoragePool,
    User,
    UserSession,
    Volume,
    WebdavService,
)

__version__ = "1.1.0"
__all__ = [
    # Client & Exceptions
    "UgreenNasClient",
    "UgreenNasError",
    "UgreenNasHttpError",
    "UgreenNasApiError",
    "UgreenNasAuthError",
    # Enums
    "FanMode",
    "UserRole",
    "RaidLevel",
    "SshStatus",
    # Models
    "NasResource",
    "User",
    "Group",
    "UserSession",
    "NetworkInterface",
    "GeneralNetworkSettings",
    "Disk",
    "StoragePool",
    "Volume",
    "SharedFolder",
    "FileService",
    "SmbService",
    "NfsService",
    "FtpService",
    "WebdavService",
    "RsyncService",
    "PowerSettings",
    "FanControl",
    "SshTerminal",
    # Managers
    "UserManager",
    "GroupManager",
    "NetworkManager",
    "NetworkInterfaceManager",
    "StorageManager",
    "DiskManager",
    "StoragePoolManager",
    "VolumeManager",
    "ShareManager",
    "ServicesManager",
    "PowerManager",
]
