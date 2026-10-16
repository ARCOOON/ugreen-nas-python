"""Network management controller for UGREEN NAS."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .client import UgreenNasClient


class NetworkController:
    """Manage network interfaces, IP settings, DNS, gateways, and bonds."""

    def __init__(self, client: UgreenNasClient):
        self._client = client

    def list_interfaces(self) -> list[dict[str, Any]]:
        """List all physical and virtual network interfaces and their IP/link statuses."""
        res = self._client.request("GET", "/ugreen/v1/network/iface/list")
        return res.get("data", {}).get("ifaces", [])

    def get_interface(self, iface_name: str) -> dict[str, Any] | None:
        """Get details for a specific interface by name (e.g. 'eth0')."""
        ifaces = self.list_interfaces()
        for iface in ifaces:
            if iface.get("interface") == iface_name:
                return iface
        return None

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

    def get_general_settings(self) -> dict[str, Any]:
        """Get general network settings including DNS servers and default gateways."""
        res = self._client.request("GET", "/ugreen/v1/network/general/get")
        return res.get("data", {}).get("general", {})

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
        """Get status of bonded/teamed network interfaces."""
        res = self._client.request("GET", "/ugreen/v1/network/bond/status")
        return res.get("data", {})

    def get_bridge_status(self) -> dict[str, Any]:
        """Get status of network bridges."""
        res = self._client.request("GET", "/ugreen/v1/network/bridge/status")
        return res.get("data", {})
