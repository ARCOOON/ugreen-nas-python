"""Storage and disk management controller for UGREEN NAS."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .client import UgreenNasClient


class StorageController:
    """Manage physical drives, SMART health data, RAID storage pools, and volumes."""

    def __init__(self, client: UgreenNasClient):
        self._client = client

    def list_disks(self) -> list[dict[str, Any]]:
        """List all physical storage drives (SATA HDDs, NVMe SSDs), slot, temperature, and health."""
        res = self._client.request("GET", "/ugreen/v2/storage/disk/list")
        return res.get("data", {}).get("result", [])

    def get_disk_smart_info(self, disk_name: str) -> dict[str, Any]:
        """Get S.M.A.R.T. health test results and attributes for a drive (e.g. 'sda')."""
        res = self._client.request("GET", f"/ugreen/v1/storage/disk/smart/info?disk={disk_name}")
        return res.get("data", {})

    def list_storage_pools(self) -> list[dict[str, Any]]:
        """List all storage pools, RAID level (RAID1, RAID5, JBOD), sync progress, and capacity."""
        res = self._client.request("GET", "/ugreen/v1/storage/pool/list")
        return res.get("data", {}).get("result", [])

    def list_volumes(self) -> list[dict[str, Any]]:
        """List all logical volumes (filesystem, total capacity, used space, mount device)."""
        res = self._client.request("GET", "/ugreen/v1/storage/volume/list")
        return res.get("data", {}).get("result", [])

    def get_volumes_summary(self) -> list[dict[str, Any]]:
        """Get summarized volume allocations for file manager."""
        res = self._client.request("GET", "/ugreen/v1/filemgr/getVolumes")
        return res.get("data", {}).get("result", [])

    def get_path_free_size(self, path: str) -> int:
        """Get available free space in bytes for a specific volume path."""
        res = self._client.request("POST", "/ugreen/v1/filemgr/getPathFreeSize", json_data={"path": path})
        return res.get("data", {}).get("free", 0)
