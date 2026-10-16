"""Share and network protocol file service controller for UGREEN NAS."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .client import UgreenNasClient


class SharesController:
    """Manage shared folders and file sharing services (SMB, NFS, FTP, WebDAV, Rsync)."""

    def __init__(self, client: UgreenNasClient):
        self._client = client

    def list_shares(self) -> list[dict[str, Any]]:
        """List all shared network folders, volume mount points, and permissions."""
        res = self._client.request("GET", "/ugreen/v1/filemgr/getShareList")
        return res.get("data", {}).get("result", [])

    def get_share_users(self, share_id: int) -> list[dict[str, Any]]:
        """List users and their access permissions for a specific share."""
        res = self._client.request("GET", f"/ugreen/v1/filemgr/shareUserList?id={share_id}")
        return res.get("data", {}).get("result", [])

    def set_share_permissions(self, share_id: int, permissions: list[dict[str, Any]]) -> dict[str, Any]:
        """Update user/group access permissions for a shared folder."""
        payload = {"id": share_id, "permissions": permissions}
        return self._client.request("POST", "/ugreen/v1/filemgr/sharePermission", json_data=payload)

    # SMB / CIFS
    def get_smb_config(self) -> dict[str, Any]:
        """Get SMB/Samba network share service configuration."""
        res = self._client.request("GET", "/ugreen/v1/file/smb/config")
        return res.get("data", {})

    def set_smb_enabled(self, enabled: bool) -> dict[str, Any]:
        """Enable or disable SMB file sharing service."""
        endpoint = "/ugreen/v1/file/smb/start" if enabled else "/ugreen/v1/file/smb/stop"
        return self._client.request("POST", endpoint)

    # NFS
    def get_nfs_config(self) -> dict[str, Any]:
        """Get NFS file sharing service configuration."""
        res = self._client.request("GET", "/ugreen/v1/file/nfs/config")
        return res.get("data", {})

    def set_nfs_enabled(self, enabled: bool) -> dict[str, Any]:
        """Enable or disable NFS service."""
        endpoint = "/ugreen/v1/file/nfs/start" if enabled else "/ugreen/v1/file/nfs/stop"
        return self._client.request("POST", endpoint)

    # FTP
    def get_ftp_config(self) -> dict[str, Any]:
        """Get FTP service configuration."""
        res = self._client.request("GET", "/ugreen/v1/file/ftp/config")
        return res.get("data", {})

    def set_ftp_enabled(self, enabled: bool) -> dict[str, Any]:
        """Enable or disable FTP service."""
        endpoint = "/ugreen/v1/file/ftp/start" if enabled else "/ugreen/v1/file/ftp/stop"
        return self._client.request("POST", endpoint)

    # WebDAV
    def get_webdav_config(self) -> dict[str, Any]:
        """Get WebDAV service configuration."""
        res = self._client.request("GET", "/ugreen/v1/file/webdav/config")
        return res.get("data", {})

    def set_webdav_enabled(self, enabled: bool) -> dict[str, Any]:
        """Enable or disable WebDAV service."""
        endpoint = "/ugreen/v1/file/webdav/start" if enabled else "/ugreen/v1/file/webdav/stop"
        return self._client.request("POST", endpoint)

    # Rsync
    def get_rsync_config(self) -> dict[str, Any]:
        """Get Rsync daemon configuration."""
        res = self._client.request("GET", "/ugreen/v1/file/rsync/config")
        return res.get("data", {})

    def set_rsync_enabled(self, enabled: bool) -> dict[str, Any]:
        """Enable or disable Rsync service."""
        endpoint = "/ugreen/v1/file/rsync/start" if enabled else "/ugreen/v1/file/rsync/stop"
        return self._client.request("POST", endpoint)
