"""Network OOP manager."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..models.network import GeneralNetworkSettings, NetworkInterface

if TYPE_CHECKING:
    from ..client import UgreenNasClient


class NetworkInterfaceManager:
    """Sub-manager for physical and virtual network interfaces."""

    def __init__(self, client: UgreenNasClient):
        self._client = client

    def all(self) -> list[NetworkInterface]:
        """List all network interfaces."""
        res = self._client.request("GET", "/ugreen/v1/network/iface/list")
        raw_list = res.get("data", {}).get("ifaces", [])
        return [NetworkInterface(self._client, item) for item in raw_list]

    def get(self, name: str) -> NetworkInterface | None:
        """Get network interface by name (e.g. 'eth0', 'eth1')."""
        for iface in self.all():
            if iface.name == name:
                return iface
        return None


class NetworkManager:
    """Manages NAS network interfaces, IP configuration, DNS, and gateways."""

    def __init__(self, client: UgreenNasClient):
        self._client = client
        self.interfaces = NetworkInterfaceManager(client)

    def get(self, iface_name: str) -> NetworkInterface | None:
        """Shorthand to get interface by name."""
        return self.interfaces.get(iface_name)

    def all_interfaces(self) -> list[NetworkInterface]:
        """Shorthand to list all interfaces."""
        return self.interfaces.all()

    def configure_interface(
        self,
        iface_name: str,
        dhcp: bool = True,
        ip: str = "",
        subnet_mask: str = "",
        gateway: str = "",
        mtu: int = 1500,
        dns: list[str] | None = None,
    ) -> dict[str, Any]:
        """Configure interface IPv4 address settings (DHCP or static IP)."""
        payload: dict[str, Any] = {
            "interface": iface_name,
            "mtu": mtu,
            "ipv4": {
                "auto": dhcp,
                "ipaddr": ip if not dhcp else "",
                "netmask": subnet_mask if not dhcp else "",
                "gateway": gateway if not dhcp else "",
                "dns": dns or [],
            },
        }
        return self._client.request("POST", "/ugreen/v1/network/iface/set", json_data=payload)

    def get_general_settings(self) -> GeneralNetworkSettings:
        """Get general network settings (DNS, priority, gateways)."""
        res = self._client.request("GET", "/ugreen/v1/network/general/get")
        return GeneralNetworkSettings(self._client, res.get("data", {}).get("general", {}))

    def set_general_settings(
        self,
        dns: list[str] | None = None,
        dns_mode: int = 1,
        prior_ipv4: int = 1,
    ) -> dict[str, Any]:
        """Update general network settings (DNS servers, priority)."""
        payload: dict[str, Any] = {
            "dns": dns or [],
            "dns_mode": dns_mode,
            "prior_ipv4": prior_ipv4,
        }
        return self._client.request("POST", "/ugreen/v1/network/general/set", json_data=payload)

    def get_gateways(self) -> dict[str, Any]:
        """List active IPv4 and IPv6 gateways."""
        res = self._client.request("GET", "/ugreen/v1/network/general/gateway_get")
        return res.get("data", {})

    def set_default_gateway(self, iface_name: str, gateway_ip: str) -> dict[str, Any]:
        """Set default network gateway interface and IP."""
        payload = {"interface": iface_name, "ipaddr": gateway_ip}
        return self._client.request("POST", "/ugreen/v1/network/general/gateway_set", json_data=payload)

    def get_bond_status(self) -> dict[str, Any]:
        """Get status of bonded network interfaces."""
        res = self._client.request("GET", "/ugreen/v1/network/bond/status")
        return res.get("data", {})

    def get_bridge_status(self) -> dict[str, Any]:
        """Get status of network bridges."""
        res = self._client.request("GET", "/ugreen/v1/network/bridge/status")
        return res.get("data", {})
