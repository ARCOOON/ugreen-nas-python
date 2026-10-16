"""Shared folder and file service domain models."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base import NasResource

if TYPE_CHECKING:
    from ..client import UgreenNasClient


class SharedFolder(NasResource):
    """Represents a shared network folder on the NAS."""

    @property
    def id(self) -> int:
        return self._raw.get("id", 0)

    @property
    def name(self) -> str:
        return self._raw.get("name", "")

    @property
    def path(self) -> str:
        return self._raw.get("path", "")

    @property
    def is_mounted(self) -> bool:
        return bool(self._raw.get("is_mount", True))

    @property
    def volume(self) -> str:
        parts = self.path.strip("/").split("/")
        return parts[0] if parts else ""

    def get_users(self) -> list[dict[str, Any]]:
        """List users and their access rights for this share."""
        return self._client.shares.get_share_users(self.id)

    def set_permissions(self, permissions: list[dict[str, Any]]) -> dict[str, Any]:
        """Update access permissions for users/groups on this share."""
        return self._client.shares.set_share_permissions(self.id, permissions)

    def __repr__(self) -> str:
        return f"<SharedFolder name='{self.name}' path='{self.path}' mounted={self.is_mounted}>"


class FileService(NasResource):
    """Base class for file sharing network services."""

    def __init__(self, client: UgreenNasClient, service_name: str):
        super().__init__(client, {})
        self.service_name = service_name

    def refresh(self) -> None:
        pass


class SmbService(FileService):
    """SMB / CIFS file sharing service."""

    def __init__(self, client: UgreenNasClient):
        super().__init__(client, "smb")

    def get_config(self) -> dict[str, Any]:
        cfg = self._client.shares.get_smb_config()
        self._refresh(cfg)
        return cfg

    @property
    def is_enabled(self) -> bool:
        return bool(self.get_config().get("status", False))

    @property
    def workgroup(self) -> str:
        return self.get_config().get("work_group", "WORKGROUP")

    def enable(self) -> bool:
        self._client.shares.set_smb_enabled(True)
        return True

    def disable(self) -> bool:
        self._client.shares.set_smb_enabled(False)
        return True

    def __repr__(self) -> str:
        return f"<SmbService enabled={self.is_enabled} workgroup='{self.workgroup}'>"


class NfsService(FileService):
    """NFS file sharing service."""

    def __init__(self, client: UgreenNasClient):
        super().__init__(client, "nfs")

    def get_config(self) -> dict[str, Any]:
        cfg = self._client.shares.get_nfs_config()
        self._refresh(cfg)
        return cfg

    @property
    def is_enabled(self) -> bool:
        return bool(self.get_config().get("enableNfsServer", False))

    def enable(self) -> bool:
        self._client.shares.set_nfs_enabled(True)
        return True

    def disable(self) -> bool:
        self._client.shares.set_nfs_enabled(False)
        return True

    def __repr__(self) -> str:
        return f"<NfsService enabled={self.is_enabled}>"


class FtpService(FileService):
    """FTP file sharing service."""

    def __init__(self, client: UgreenNasClient):
        super().__init__(client, "ftp")

    def get_config(self) -> dict[str, Any]:
        cfg = self._client.shares.get_ftp_config()
        self._refresh(cfg)
        return cfg

    def enable(self) -> bool:
        self._client.shares.set_ftp_enabled(True)
        return True

    def disable(self) -> bool:
        self._client.shares.set_ftp_enabled(False)
        return True


class WebdavService(FileService):
    """WebDAV file sharing service."""

    def __init__(self, client: UgreenNasClient):
        super().__init__(client, "webdav")

    def get_config(self) -> dict[str, Any]:
        cfg = self._client.shares.get_webdav_config()
        self._refresh(cfg)
        return cfg

    def enable(self) -> bool:
        self._client.shares.set_webdav_enabled(True)
        return True

    def disable(self) -> bool:
        self._client.shares.set_webdav_enabled(False)
        return True


class RsyncService(FileService):
    """Rsync daemon service."""

    def __init__(self, client: UgreenNasClient):
        super().__init__(client, "rsync")

    def get_config(self) -> dict[str, Any]:
        cfg = self._client.shares.get_rsync_config()
        self._refresh(cfg)
        return cfg

    def enable(self) -> bool:
        self._client.shares.set_rsync_enabled(True)
        return True

    def disable(self) -> bool:
        self._client.shares.set_rsync_enabled(False)
        return True
