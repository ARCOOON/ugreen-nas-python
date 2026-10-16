"""User and group management controller for UGREEN NAS."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .crypto import rsa_encrypt_pkcs1_v15

if TYPE_CHECKING:
    from .client import UgreenNasClient


class UsersController:
    """Manage NAS local users, groups, quotas, permissions, and active login sessions."""

    def __init__(self, client: UgreenNasClient):
        self._client = client

    def list_users(self, reverse: bool = False) -> list[dict[str, Any]]:
        """List all users on the NAS."""
        res = self._client.request("GET", f"/ugreen/v1/user/list?reverse={str(reverse).lower()}")
        return res.get("data", {}).get("list", [])

    def get_user_by_uid(self, uid: int) -> dict[str, Any]:
        """Get details for a user by UID."""
        res = self._client.request("GET", f"/ugreen/v1/user/uid/{uid}")
        return res.get("data", {})

    def get_current_user(self) -> dict[str, Any]:
        """Get profile of the currently logged-in user."""
        res = self._client.request("GET", "/ugreen/v1/user/current/user")
        return res.get("data", {})

    def list_online_sessions(self) -> list[dict[str, Any]]:
        """List currently active user sessions."""
        res = self._client.request("GET", "/ugreen/v1/user/online/list")
        return res.get("data", {}).get("list", [])

    def terminate_session(self, session_id: str) -> dict[str, Any]:
        """Terminate / disconnect an active user session."""
        return self._client.request("POST", "/ugreen/v1/user/online/stop", json_data={"id": session_id})

    def create_user(
        self,
        username: str,
        password: str,
        role: str = "users",
        groups: list[int] | None = None,
        email: str = "",
        phone: str = "",
        description: str = "",
        dir_quota: int = 0,
        expire_time: int = -1,
    ) -> dict[str, Any]:
        """Create a new local user on the NAS."""
        payload = {
            "username": username,
            "password": password,
            "role": role,
            "groups": groups or [100],  # 100 = default users group
            "email": email,
            "phone": phone,
            "description": description,
            "dir_quota": dir_quota,
            "expire_time": expire_time,
            "enable_home_dir": True,
        }
        return self._client.request("POST", "/ugreen/v1/user/create", json_data=payload)

    def edit_user(
        self,
        uid: int,
        role: str | None = None,
        groups: list[int] | None = None,
        email: str | None = None,
        phone: str | None = None,
        description: str | None = None,
        dir_quota: int | None = None,
    ) -> dict[str, Any]:
        """Update an existing user's details."""
        user = self.get_user_by_uid(uid)
        payload = {
            "uid": uid,
            "username": user.get("username"),
            "role": role if role is not None else user.get("role", "users"),
            "groups": groups if groups is not None else [g.get("gid") for g in user.get("groups", [])],
            "email": email if email is not None else user.get("email", ""),
            "phone": phone if phone is not None else user.get("phone", ""),
            "description": description if description is not None else user.get("description", ""),
            "dir_quota": dir_quota if dir_quota is not None else user.get("dir_quota", 0),
        }
        return self._client.request("POST", "/ugreen/v1/user/edit", json_data=payload)

    def delete_users(self, uids: list[int], admin_password: str) -> dict[str, Any]:
        """Delete one or more users by UID.

        Requires the current administrator password for confirmation.
        """
        curr_user = self.get_current_user()
        admin_username = curr_user.get("username") or self._client.login_info.get("username", "")

        rsa_token = self._client.get_rsa_public_key(admin_username)
        encrypted_admin_pw = rsa_encrypt_pkcs1_v15(admin_password, rsa_token)

        headers = {"X-CurPass-Token": encrypted_admin_pw}
        return self._client.request(
            "DELETE",
            "/ugreen/v1/user/delete",
            json_data={"uids": uids},
            headers=headers,
        )

    def list_groups(self, reverse: bool = False) -> list[dict[str, Any]]:
        """List all user groups."""
        res = self._client.request("GET", f"/ugreen/v1/group/list?reverse={str(reverse).lower()}")
        return res.get("data", {}).get("list", [])

    def get_group(self, gid: int) -> dict[str, Any]:
        """Get details for a group by GID."""
        res = self._client.request("GET", f"/ugreen/v1/group/info/{gid}")
        return res.get("data", {})

    def create_group(self, name: str, description: str = "", members: list[int] | None = None) -> dict[str, Any]:
        """Create a new user group."""
        payload = {"name": name, "description": description, "members": members or []}
        return self._client.request("POST", "/ugreen/v1/group/create", json_data=payload)

    def edit_group(
        self,
        gid: int,
        name: str,
        description: str = "",
        members: list[int] | None = None,
    ) -> dict[str, Any]:
        """Edit an existing user group."""
        payload = {"gid": gid, "name": name, "description": description, "members": members or []}
        return self._client.request("POST", "/ugreen/v1/group/edit", json_data=payload)

    def delete_group(self, gid: int) -> dict[str, Any]:
        """Delete a group by GID."""
        return self._client.request("DELETE", "/ugreen/v1/group/delete", json_data={"gid": gid})
