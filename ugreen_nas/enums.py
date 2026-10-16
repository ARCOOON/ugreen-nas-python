"""Enums for UGREEN NAS domain objects."""

from enum import Enum, IntEnum


class FanMode(IntEnum):
    """Fan operating profile."""
    QUIET = 1
    STANDARD = 2
    FULL_SPEED = 3


class UserRole(str, Enum):
    """User privilege role."""
    ADMIN = "admin"
    USERS = "users"


class RaidLevel(str, Enum):
    """Storage pool RAID levels."""
    RAID0 = "raid0"
    RAID1 = "raid1"
    RAID5 = "raid5"
    RAID6 = "raid6"
    RAID10 = "raid10"
    JBOD = "jbod"
    SINGLE = "single"


class SshStatus(IntEnum):
    """SSH daemon status."""
    ENABLED = 1
    DISABLED = 2
