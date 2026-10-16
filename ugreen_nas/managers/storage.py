"""Storage OOP manager."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models.storage import Disk, StoragePool, Volume

if TYPE_CHECKING:
    from ..client import UgreenNasClient


class DiskManager:
    """Sub-manager for physical drives."""

    def __init__(self, client: UgreenNasClient):
        self._client = client

    def all(self) -> list[Disk]:
        """List all physical storage drives."""
        res = self._client.request("GET", "/ugreen/v2/storage/disk/list")
        raw_list = res.get("data", {}).get("result", [])
        return [Disk(self._client, item) for item in raw_list]

    def get(self, slot_or_name: str) -> Disk | None:
        """Find a drive by dev name (e.g. 'sda') or slot (e.g. '1')."""
        for d in self.all():
            if d.name == slot_or_name or d.slot == str(slot_or_name) or d.dev_name == slot_or_name:
                return d
        return None


class StoragePoolManager:
    """Sub-manager for RAID storage pools."""

    def __init__(self, client: UgreenNasClient):
        self._client = client

    def all(self) -> list[StoragePool]:
        """List all RAID storage pools."""
        res = self._client.request("GET", "/ugreen/v1/storage/pool/list")
        raw_list = res.get("data", {}).get("result", [])
        return [StoragePool(self._client, item) for item in raw_list]

    def get(self, name_or_label: str) -> StoragePool | None:
        """Find a storage pool by name or label."""
        for p in self.all():
            if p.name == name_or_label or p.label == name_or_label:
                return p
        return None


class VolumeManager:
    """Sub-manager for logical volumes."""

    def __init__(self, client: UgreenNasClient):
        self._client = client

    def all(self) -> list[Volume]:
        """List all logical volumes."""
        res = self._client.request("GET", "/ugreen/v1/storage/volume/list")
        raw_list = res.get("data", {}).get("result", [])
        return [Volume(self._client, item) for item in raw_list]

    def get(self, name_or_uuid: str) -> Volume | None:
        """Find a volume by name (e.g. 'dm-0', 'volume1') or UUID."""
        for v in self.all():
            if v.name == name_or_uuid or v.uuid == name_or_uuid or v.label == name_or_uuid:
                return v
        return None


class StorageManager:
    """Manages physical disks, RAID pools, and volumes."""

    def __init__(self, client: UgreenNasClient):
        self._client = client
        self.disks = DiskManager(client)
        self.pools = StoragePoolManager(client)
        self.volumes = VolumeManager(client)

    def get_disk_smart_info(self, disk_name: str) -> dict[str, Any]:
        """Get S.M.A.R.T. health test results and attributes for a drive (e.g. 'sda')."""
        res = self._client.request("GET", f"/ugreen/v1/storage/disk/smart/info?disk={disk_name}")
        return res.get("data", {})

    def get_path_free_size(self, path: str) -> int:
        """Get available free space in bytes for a specific volume path."""
        res = self._client.request("POST", "/ugreen/v1/filemgr/getPathFreeSize", json_data={"path": path})
        return res.get("data", {}).get("free", 0)

    def get_volumes_summary(self) -> list[dict[str, Any]]:
        """Get summarized volume allocations."""
        res = self._client.request("GET", "/ugreen/v1/filemgr/getVolumes")
        return res.get("data", {}).get("result", [])
