"""Shared folders OOP manager."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models.shares import SharedFolder

if TYPE_CHECKING:
    from ..client import UgreenNasClient


class ShareManager:
    """Manages shared folders and share permissions."""

    def __init__(self, client: UgreenNasClient):
        self._client = client

    def all(self) -> list[SharedFolder]:
        """List all shared network folders."""
        res = self._client.request("GET", "/ugreen/v1/filemgr/getShareList")
        raw_list = res.get("data", {}).get("result", [])
        return [SharedFolder(self._client, item) for item in raw_list]

    def get(self, id_or_name: int | str) -> SharedFolder | None:
        """Find a shared folder by ID or name."""
        for s in self.all():
            if isinstance(id_or_name, int) and s.id == id_or_name:
                return s
            if isinstance(id_or_name, str) and (s.name == id_or_name or str(s.id) == id_or_name):
                return s
        return None

    def get_share_users(self, share_id: int) -> list[dict[str, Any]]:
        """List users and their access permissions for a specific share."""
        res = self._client.request("GET", f"/ugreen/v1/filemgr/shareUserList?id={share_id}")
        return res.get("data", {}).get("result", [])

    def set_share_permissions(self, share_id: int, permissions: list[dict[str, Any]]) -> dict[str, Any]:
        """Update user/group access permissions for a shared folder."""
        payload = {"id": share_id, "permissions": permissions}
        return self._client.request("POST", "/ugreen/v1/filemgr/sharePermission", json_data=payload)

    # Underlying service helpers called by FileService models
    def get_smb_config(self) -> dict[str, Any]:
        return self._client.request("GET", "/ugreen/v1/file/smb/config").get("data", {})

    def set_smb_enabled(self, enabled: bool) -> dict[str, Any]:
        endpoint = "/ugreen/v1/file/smb/start" if enabled else "/ugreen/v1/file/smb/stop"
        return self._client.request("POST", endpoint)

    def get_nfs_config(self) -> dict[str, Any]:
        return self._client.request("GET", "/ugreen/v1/file/nfs/config").get("data", {})

    def set_nfs_enabled(self, enabled: bool) -> dict[str, Any]:
        endpoint = "/ugreen/v1/file/nfs/start" if enabled else "/ugreen/v1/file/nfs/stop"
        return self._client.request("POST", endpoint)

    def get_ftp_config(self) -> dict[str, Any]:
        return self._client.request("GET", "/ugreen/v1/file/ftp/config").get("data", {})

    def set_ftp_enabled(self, enabled: bool) -> dict[str, Any]:
        endpoint = "/ugreen/v1/file/ftp/start" if enabled else "/ugreen/v1/file/ftp/stop"
        return self._client.request("POST", endpoint)

    def get_webdav_config(self) -> dict[str, Any]:
        return self._client.request("GET", "/ugreen/v1/file/webdav/config").get("data", {})

    def set_webdav_enabled(self, enabled: bool) -> dict[str, Any]:
        endpoint = "/ugreen/v1/file/webdav/start" if enabled else "/ugreen/v1/file/webdav/stop"
        return self._client.request("POST", endpoint)

    def get_rsync_config(self) -> dict[str, Any]:
        return self._client.request("GET", "/ugreen/v1/file/rsync/config").get("data", {})

    def set_rsync_enabled(self, enabled: bool) -> dict[str, Any]:
        endpoint = "/ugreen/v1/file/rsync/start" if enabled else "/ugreen/v1/file/rsync/stop"
        return self._client.request("POST", endpoint)
