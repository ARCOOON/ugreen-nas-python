"""User and Group OOP managers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..crypto import rsa_encrypt_pkcs1_v15
from ..models.users import Group, User, UserSession

if TYPE_CHECKING:
    from ..client import UgreenNasClient


class UserManager:
    """Manages NAS users and active user sessions."""

    def __init__(self, client: UgreenNasClient):
        self._client = client

    def all(self, reverse: bool = False) -> list[User]:
        """List all users on the NAS as rich User objects."""
        res = self._client.request("GET", f"/ugreen/v1/user/list?reverse={str(reverse).lower()}")
        raw_list = res.get("data", {}).get("list", [])
        return [User(self._client, item) for item in raw_list]

    def get(self, uid: int) -> User | None:
        """Get a user by UID."""
        res = self._client.request("GET", f"/ugreen/v1/user/uid/{uid}")
        data = res.get("data")
        return User(self._client, data) if data else None

    def get_by_name(self, username: str) -> User | None:
        """Find a user by username."""
        for u in self.all():
            if u.username == username:
                return u
        return None

    def current(self) -> User:
        """Get profile of the currently logged-in user."""
        res = self._client.request("GET", "/ugreen/v1/user/current/user")
        return User(self._client, res.get("data", {}))

    def create(
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
    ) -> User:
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
        res = self._client.request("POST", "/ugreen/v1/user/create", json_data=payload)
        user_obj = self.get_by_name(username)
        if user_obj:
            return user_obj
        return User(self._client, res.get("data", {"username": username, "role": role}))

    def edit(
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
        curr = self.get(uid)
        curr_raw = curr.raw if curr else {}
        payload = {
            "uid": uid,
            "username": curr_raw.get("username"),
            "role": role if role is not None else curr_raw.get("role", "users"),
            "groups": groups if groups is not None else [g.get("gid") for g in curr_raw.get("groups", [])],
            "email": email if email is not None else curr_raw.get("email", ""),
            "phone": phone if phone is not None else curr_raw.get("phone", ""),
            "description": description if description is not None else curr_raw.get("description", ""),
            "dir_quota": dir_quota if dir_quota is not None else curr_raw.get("dir_quota", 0),
        }
        return self._client.request("POST", "/ugreen/v1/user/edit", json_data=payload)

    def delete(self, uids: int | list[int], admin_password: str) -> bool:
        """Delete one or more users by UID. Requires current administrator password."""
        uid_list = [uids] if isinstance(uids, int) else uids
        curr_user = self.current()
        admin_username = curr_user.username or self._client.login_info.get("username", "")

        rsa_token = self._client.get_rsa_public_key(admin_username)
        encrypted_admin_pw = rsa_encrypt_pkcs1_v15(admin_password, rsa_token)

        headers = {"X-CurPass-Token": encrypted_admin_pw}
        res = self._client.request(
            "DELETE",
            "/ugreen/v1/user/delete",
            json_data={"uids": uid_list},
            headers=headers,
        )
        return res.get("code") == 200

    def sessions(self, page_num: int = 1, page_size: int = 50) -> list[UserSession]:
        """List active user sessions."""
        res = self._client.request(
            "POST",
            "/ugreen/v1/user/online/list",
            json_data={"page_num": page_num, "page_size": page_size},
        )
        raw_list = res.get("data", {}).get("list", [])
        return [UserSession(self._client, item) for item in raw_list]

    def terminate_session(self, session_id: int | str) -> bool:
        """Terminate / disconnect an active user session."""
        res = self._client.request("POST", "/ugreen/v1/user/online/stop", json_data={"id": int(session_id)})
        return res.get("code") == 200


class GroupManager:
    """Manages NAS user groups."""

    def __init__(self, client: UgreenNasClient):
        self._client = client

    def all(self, reverse: bool = False) -> list[Group]:
        """List all user groups."""
        res = self._client.request("GET", f"/ugreen/v1/group/list?reverse={str(reverse).lower()}")
        raw_list = res.get("data", {}).get("list", [])
        return [Group(self._client, item) for item in raw_list]

    def get(self, gid: int) -> Group | None:
        """Get a group by GID."""
        res = self._client.request("GET", f"/ugreen/v1/group/info/{gid}")
        data = res.get("data")
        return Group(self._client, data) if data else None

    def get_by_name(self, name: str) -> Group | None:
        """Find a group by name."""
        for g in self.all():
            if g.name == name:
                return g
        return None

    def create(self, name: str, description: str = "", members: list[int] | None = None) -> Group:
        """Create a new user group."""
        payload = {"name": name, "description": description, "members": members or []}
        res = self._client.request("POST", "/ugreen/v1/group/create", json_data=payload)
        grp = self.get_by_name(name)
        if grp:
            return grp
        return Group(self._client, res.get("data", {"name": name, "description": description}))

    def edit(self, gid: int, name: str, description: str = "", members: list[int] | None = None) -> dict[str, Any]:
        """Edit an existing user group."""
        payload = {"gid": gid, "name": name, "description": description, "members": members or []}
        return self._client.request("POST", "/ugreen/v1/group/edit", json_data=payload)

    def delete(self, gid: int) -> bool:
        """Delete a group by GID."""
        res = self._client.request("DELETE", "/ugreen/v1/group/delete", json_data={"gid": gid})
        return res.get("code") == 200
