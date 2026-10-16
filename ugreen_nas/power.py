"""Power and hardware management controller for UGREEN NAS."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .client import UgreenNasClient


class PowerController:
    """Manage NAS power states, fan modes, scheduled on/off, LED, buzzer, and SSH/Telnet terminal."""

    def __init__(self, client: UgreenNasClient):
        self._client = client

    def reboot(self) -> dict[str, Any]:
        """Reboot the NAS device."""
        return self._client.request("POST", "/ugreen/v1/desktop/reboot")

    def poweroff(self) -> dict[str, Any]:
        """Shutdown / power off the NAS device."""
        return self._client.request("POST", "/ugreen/v1/desktop/poweroff")

    def get_power_config(self) -> dict[str, Any]:
        """Get power-on recovery, Wake-on-LAN, scheduled power switches, and disk sleep settings."""
        res = self._client.request("GET", "/ugreen/v1/hardware/power/config")
        return res.get("data", {})

    def set_power_config(
        self,
        wake_on_lan: bool | None = None,
        power_boot_on_ac: bool | None = None,
        hard_drive_sleep_minutes: int | None = None,
        enable_scheduled_power: bool | None = None,
        time_switches: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Update power recovery, WoL, disk standby timers, and power schedules."""
        current = self.get_power_config()
        payload = {
            "wake_on": wake_on_lan if wake_on_lan is not None else current.get("wake_on", True),
            "power_boot": power_boot_on_ac if power_boot_on_ac is not None else current.get("power_boot", False),
            "hard_drive_flag": hard_drive_sleep_minutes is not None and hard_drive_sleep_minutes > 0,
            "hard_drive_time": hard_drive_sleep_minutes or current.get("hard_drive_time", 20),
            "hard_drive_unit": "M",
            "hard_drive_strategy": current.get("hard_drive_strategy", 1),
            "enable_scheduled_power": (
                enable_scheduled_power
                if enable_scheduled_power is not None
                else current.get("enable_scheduled_power", False)
            ),
            "time_switches": time_switches if time_switches is not None else current.get("time_switches", []),
        }
        return self._client.request("POST", "/ugreen/v1/hardware/power/start", json_data=payload)

    def get_fan_config(self) -> dict[str, Any]:
        """Get fan status and operating mode."""
        res = self._client.request("GET", "/ugreen/v1/hardware/fan/config")
        return res.get("data", {})

    def set_fan_mode(self, mode: int) -> dict[str, Any]:
        """Set fan speed profile: 1 = quiet, 2 = standard, 3 = full/performance."""
        return self._client.request("POST", f"/ugreen/v1/hardware/fan/setfan?mode={mode}")

    def get_terminal_config(self) -> dict[str, Any]:
        """Get SSH and Telnet daemon settings."""
        res = self._client.request("GET", "/ugreen/v1/terminal/get")
        return res.get("data", {})

    def set_ssh_config(
        self,
        enabled: bool,
        port: int = 22,
        permit_lan_access_only: bool = True,
        use_sftp: bool = True,
    ) -> dict[str, Any]:
        """Configure SSH service access and port."""
        current = self.get_terminal_config()
        ssh_cfg = current.get("SshConfig", {})
        payload = {
            "SshConfig": {
                "enable": 1 if enabled else 2,
                "port": port,
                "permitLanAccessOnly": 1 if permit_lan_access_only else 2,
                "useSftp": 1 if use_sftp else 2,
                "encryptLevel": ssh_cfg.get("encryptLevel", 3),
                "exTimeDuration": ssh_cfg.get("exTimeDuration", 3),
            },
            "TelnetConfig": current.get("TelnetConfig", {"enable": 2, "port": 23}),
        }
        return self._client.request("POST", "/ugreen/v1/terminal/set", json_data=payload)

    def get_buzzer_config(self) -> dict[str, Any]:
        """Get system buzzer alert configurations."""
        res = self._client.request("GET", "/ugreen/v1/hardware/buzzer/config")
        return res.get("data", {})

    def mute_buzzer(self) -> dict[str, Any]:
        """Mute active buzzer alert."""
        return self._client.request("POST", "/ugreen/v1/hardware/buzzer/mute")

    def get_led_config(self) -> dict[str, Any]:
        """Get hardware LED indicator settings."""
        res = self._client.request("GET", "/ugreen/v1/hardware/led/config")
        return res.get("data", {})
