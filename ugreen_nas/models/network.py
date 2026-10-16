"""Network domain models."""

from __future__ import annotations

from typing import Any

from .base import NasResource


class NetworkInterface(NasResource):
    """Represents a physical or virtual network interface on the NAS."""

    @property
    def name(self) -> str:
        return self._raw.get("interface", "")

    @property
    def is_connected(self) -> bool:
        return self._raw.get("connection", 0) == 1

    @property
    def mac_address(self) -> str:
        return self._raw.get("hardware", "")

    @property
    def duplex(self) -> str:
        return self._raw.get("duplex", "")

    @property
    def speed(self) -> int:
        return self._raw.get("speed", 0)

    @property
    def mtu(self) -> int:
        return self._raw.get("mtu", 1500)

    @property
    def ipv4(self) -> dict[str, Any]:
        return self._raw.get("ipv4", {})

    @property
    def ip(self) -> str:
        return self.ipv4.get("ipaddr", "")

    @property
    def netmask(self) -> str:
        return self.ipv4.get("netmask", "")

    @property
    def gateway(self) -> str:
        return self.ipv4.get("gateway", "")

    @property
    def dns(self) -> list[str]:
        return self.ipv4.get("dns", [])

    @property
    def is_dhcp(self) -> bool:
        return bool(self.ipv4.get("auto", True))

    def set_dhcp(self, mtu: int = 1500) -> NetworkInterface:
        """Configure interface to obtain IP via DHCP."""
        self._client.network.configure_interface(
            iface_name=self.name,
            dhcp=True,
            mtu=mtu,
        )
        updated = self._client.network.get(self.name)
        if updated:
            self._refresh(updated.raw)
        return self

    def set_static_ip(
        self,
        ip: str,
        subnet_mask: str,
        gateway: str = "",
        dns: list[str] | None = None,
        mtu: int = 1500,
    ) -> NetworkInterface:
        """Configure interface with a static IP address."""
        self._client.network.configure_interface(
            iface_name=self.name,
            dhcp=False,
            ip=ip,
            subnet_mask=subnet_mask,
            gateway=gateway,
            dns=dns,
            mtu=mtu,
        )
        updated = self._client.network.get(self.name)
        if updated:
            self._refresh(updated.raw)
        return self

    def __repr__(self) -> str:
        return (
            f"<NetworkInterface name='{self.name}' ip='{self.ip}' "
            f"mac='{self.mac_address}' connected={self.is_connected}>"
        )


class GeneralNetworkSettings(NasResource):
    """Represents global DNS and routing configurations."""

    @property
    def dns_servers(self) -> list[str]:
        return self._raw.get("dns", [])

    @property
    def dns_mode(self) -> int:
        return self._raw.get("dns_mode", 1)

    @property
    def default_gateway_ip(self) -> str:
        gw = self._raw.get("ipv4_gateway", {})
        return gw.get("ipaddr", "")

    @property
    def default_gateway_iface(self) -> str:
        gw = self._raw.get("ipv4_gateway", {})
        return gw.get("interface", "")

    def set_dns(self, dns_servers: list[str]) -> GeneralNetworkSettings:
        """Update global DNS servers."""
        self._client.network.set_general_settings(dns=dns_servers)
        new_settings = self._client.network.get_general_settings()
        self._refresh(new_settings.raw)
        return self

    def __repr__(self) -> str:
        return f"<GeneralNetworkSettings dns={self.dns_servers} gateway='{self.default_gateway_ip}'>"
