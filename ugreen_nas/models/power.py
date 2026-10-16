"""Power, hardware, and service domain models."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..enums import FanMode
from .base import NasResource

if TYPE_CHECKING:
    from ..client import UgreenNasClient


class FanControl(NasResource):
    """Controls the NAS cooling fan profile."""

    def __init__(self, client: UgreenNasClient):
        super().__init__(client, {})

    def get_config(self) -> dict[str, Any]:
        cfg = self._client.power.get_fan_config()
        self._refresh(cfg)
        return cfg

    @property
    def mode(self) -> FanMode:
        raw_mode = self.get_config().get("mode", 2)
        try:
            return FanMode(raw_mode)
        except ValueError:
            return FanMode.STANDARD

    def set_mode(self, mode: FanMode | int) -> bool:
        """Set fan speed mode: FanMode.QUIET (1), FanMode.STANDARD (2), FanMode.FULL_SPEED (3)."""
        val = int(mode)
        self._client.power.set_fan_mode(val)
        return True

    def __repr__(self) -> str:
        return f"<FanControl mode={self.mode.name}>"


class PowerSettings(NasResource):
    """Controls AC power recovery, Wake-on-LAN, scheduled switches, and hard drive sleep."""

    @property
    def wake_on_lan(self) -> bool:
        return bool(self._raw.get("wake_on", True))

    @property
    def power_boot_on_ac(self) -> bool:
        return bool(self._raw.get("power_boot", False))

    @property
    def hdd_sleep_minutes(self) -> int:
        return self._raw.get("hard_drive_time", 20) if self._raw.get("hard_drive_flag") else 0

    @property
    def scheduled_power_enabled(self) -> bool:
        return bool(self._raw.get("enable_scheduled_power", False))

    @property
    def time_switches(self) -> list[dict[str, Any]]:
        return self._raw.get("time_switches", [])

    def update(
        self,
        wake_on_lan: bool | None = None,
        power_boot_on_ac: bool | None = None,
        hdd_sleep_minutes: int | None = None,
        scheduled_power_enabled: bool | None = None,
    ) -> PowerSettings:
        """Update power and drive sleep configurations."""
        self._client.power.set_power_config(
            wake_on_lan=wake_on_lan,
            power_boot_on_ac=power_boot_on_ac,
            hard_drive_sleep_minutes=hdd_sleep_minutes,
            enable_scheduled_power=scheduled_power_enabled,
        )
        updated = self._client.power.get_settings()
        self._refresh(updated.raw)
        return self

    def __repr__(self) -> str:
        return (
            f"<PowerSettings wol={self.wake_on_lan} "
            f"ac_recovery={self.power_boot_on_ac} hdd_sleep={self.hdd_sleep_minutes}m>"
        )


class SshTerminal(NasResource):
    """Controls SSH daemon access and port."""

    def __init__(self, client: UgreenNasClient):
        super().__init__(client, {})

    def get_config(self) -> dict[str, Any]:
        cfg = self._client.power.get_terminal_config()
        self._refresh(cfg)
        return cfg.get("SshConfig", {})

    @property
    def is_enabled(self) -> bool:
        return self.get_config().get("enable") == 1

    @property
    def port(self) -> int:
        return self.get_config().get("port", 22)

    @property
    def is_lan_only(self) -> bool:
        return self.get_config().get("permitLanAccessOnly") == 1

    @property
    def sftp_enabled(self) -> bool:
        return self.get_config().get("useSftp") == 1

    def enable(self, port: int = 22, lan_only: bool = True) -> bool:
        self._client.power.set_ssh_config(enabled=True, port=port, permit_lan_access_only=lan_only)
        return True

    def disable(self) -> bool:
        self._client.power.set_ssh_config(enabled=False)
        return True

    def __repr__(self) -> str:
        return f"<SshTerminal enabled={self.is_enabled} port={self.port} lan_only={self.is_lan_only}>"
