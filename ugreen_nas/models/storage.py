"""Storage, disk, pool, and volume domain models."""

from __future__ import annotations

from typing import Any

from .base import NasResource


class Disk(NasResource):
    """Represents a physical storage drive (HDD or NVMe SSD)."""

    @property
    def name(self) -> str:
        return self._raw.get("name", "")

    @property
    def dev_name(self) -> str:
        return self._raw.get("dev_name", "")

    @property
    def model(self) -> str:
        return self._raw.get("model", "")

    @property
    def serial(self) -> str:
        return self._raw.get("serial", "")

    @property
    def size_bytes(self) -> int:
        return self._raw.get("size", 0)

    @property
    def size_gb(self) -> float:
        return round(self.size_bytes / (1024**3), 2)

    @property
    def size_tb(self) -> float:
        return round(self.size_bytes / (1024**4), 2)

    @property
    def slot(self) -> str:
        return self._raw.get("slot", "")

    @property
    def interface_type(self) -> str:
        return self._raw.get("interface_type", "")

    @property
    def temperature(self) -> int | None:
        return self._raw.get("temperature")

    @property
    def health_status(self) -> int:
        return self._raw.get("health", 0)

    @property
    def is_healthy(self) -> bool:
        return self.health_status == 0 or self._raw.get("status") == 1

    def get_smart_info(self) -> dict[str, Any]:
        """Fetch latest S.M.A.R.T. health attributes and self-test records for this drive."""
        try:
            return self._client.storage.get_disk_smart_info(self.name)
        except Exception:
            return {
                "health": self.health_status,
                "temperature": self.temperature,
                "power_on_hours": self._raw.get("power_on_hours"),
                "is_support_smart": self._raw.get("is_support_smart", True),
                "brand": self._raw.get("brand"),
                "model": self.model,
                "serial": self.serial,
            }

    def __repr__(self) -> str:
        return f"<Disk name='{self.name}' model='{self.model}' size='{self.size_tb} TB' slot='{self.slot}'>"


class StoragePool(NasResource):
    """Represents a RAID storage pool."""

    @property
    def name(self) -> str:
        return self._raw.get("name", "")

    @property
    def label(self) -> str:
        return self._raw.get("label", "")

    @property
    def raid_level(self) -> str:
        return self._raw.get("level", "")

    @property
    def status(self) -> int:
        return self._raw.get("status", 0)

    @property
    def is_healthy(self) -> bool:
        return self.status == 0

    @property
    def is_syncing(self) -> bool:
        return bool(self._raw.get("sys_sync_progress", 0) > 0)

    @property
    def sync_progress_percent(self) -> float:
        return float(self._raw.get("sys_sync_progress", 0))

    @property
    def total_bytes(self) -> int:
        return self._raw.get("total", 0)

    @property
    def total_gb(self) -> float:
        return round(self.total_bytes / (1024**3), 2)

    @property
    def total_tb(self) -> float:
        return round(self.total_bytes / (1024**4), 2)

    def __repr__(self) -> str:
        return (
            f"<StoragePool name='{self.name}' level='{self.raid_level}' "
            f"total='{self.total_tb} TB' healthy={self.is_healthy}>"
        )


class Volume(NasResource):
    """Represents a logical storage volume."""

    @property
    def name(self) -> str:
        return self._raw.get("name", "")

    @property
    def label(self) -> str:
        return self._raw.get("label", "")

    @property
    def filesystem(self) -> str:
        return self._raw.get("filesystem", "")

    @property
    def uuid(self) -> str:
        return self._raw.get("uuid", "")

    @property
    def device(self) -> str:
        return self._raw.get("device", "")

    @property
    def total_bytes(self) -> int:
        return self._raw.get("total", 0)

    @property
    def used_bytes(self) -> int:
        return self._raw.get("used", 0)

    @property
    def free_bytes(self) -> int:
        return max(0, self.total_bytes - self.used_bytes)

    @property
    def total_gb(self) -> float:
        return round(self.total_bytes / (1024**3), 2)

    @property
    def used_gb(self) -> float:
        return round(self.used_bytes / (1024**3), 2)

    @property
    def free_gb(self) -> float:
        return round(self.free_bytes / (1024**3), 2)

    @property
    def total_tb(self) -> float:
        return round(self.total_bytes / (1024**4), 2)

    @property
    def used_tb(self) -> float:
        return round(self.used_bytes / (1024**4), 2)

    @property
    def usage_percent(self) -> float:
        if self.total_bytes == 0:
            return 0.0
        return round((self.used_bytes / self.total_bytes) * 100, 1)

    @property
    def is_healthy(self) -> bool:
        return self._raw.get("health", 0) == 0

    def get_path_free_size(self, subpath: str = "") -> int:
        """Get available free space under a path in this volume."""
        target_path = f"/{self.name}/{subpath.lstrip('/')}".rstrip("/")
        return self._client.storage.get_path_free_size(target_path)

    def __repr__(self) -> str:
        return (
            f"<Volume name='{self.name}' fs='{self.filesystem}' "
            f"used='{self.used_gb}GB/{self.total_tb}TB ({self.usage_percent}%)'>"
        )
