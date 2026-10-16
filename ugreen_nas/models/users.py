"""User, group, and session domain models."""

from __future__ import annotations

from typing import Any

from .base import NasResource


class User(NasResource):
    """Represents a local user on the UGREEN NAS."""

    @property
    def uid(self) -> int:
        return self._raw.get("uid", 0)

    @property
    def username(self) -> str:
        return self._raw.get("username", "")

    @property
    def role(self) -> str:
        return self._raw.get("role", "users")

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    @property
    def email(self) -> str:
        return self._raw.get("email", "")

    @property
    def phone(self) -> str:
        return self._raw.get("phone", "")

    @property
    def description(self) -> str:
        return self._raw.get("description", "")

    @property
    def dir_quota_bytes(self) -> int:
        return self._raw.get("dir_quota", 0)

    @property
    def is_expired(self) -> bool:
        return self._raw.get("is_expired", False)

    @property
    def groups(self) -> list[dict[str, Any]]:
        return self._raw.get("groups", [])

    def edit(
        self,
        role: str | None = None,
        groups: list[int] | None = None,
        email: str | None = None,
        phone: str | None = None,
        description: str | None = None,
        dir_quota: int | None = None,
    ) -> User:
        """Update this user's attributes."""
        self._client.users.edit(
            uid=self.uid,
            role=role,
            groups=groups,
            email=email,
            phone=phone,
            description=description,
            dir_quota=dir_quota,
        )
        # reload updated user
        updated = self._client.users.get(self.uid)
        if updated:
            self._refresh(updated.raw)
        return self

    def delete(self, admin_password: str) -> bool:
        """Delete this user from the NAS. Requires current admin password."""
        return self._client.users.delete(self.uid, admin_password=admin_password)

    def __repr__(self) -> str:
        return f"<User username='{self.username}' uid={self.uid} role='{self.role}'>"


class Group(NasResource):
    """Represents a local user group on the UGREEN NAS."""

    @property
    def gid(self) -> int:
        return self._raw.get("gid", 0)

    @property
    def name(self) -> str:
        return self._raw.get("name", "")

    @property
    def description(self) -> str:
        return self._raw.get("description", "")

    @property
    def members(self) -> list[int]:
        return self._raw.get("members", [])

    def edit(
        self,
        name: str | None = None,
        description: str | None = None,
        members: list[int] | None = None,
    ) -> Group:
        """Update this group's attributes."""
        self._client.groups.edit(
            gid=self.gid,
            name=name or self.name,
            description=description if description is not None else self.description,
            members=members if members is not None else self.members,
        )
        updated = self._client.groups.get(self.gid)
        if updated:
            self._refresh(updated.raw)
        return self

    def delete(self) -> bool:
        """Delete this group from the NAS."""
        return self._client.groups.delete(self.gid)

    def __repr__(self) -> str:
        return f"<Group name='{self.name}' gid={self.gid}>"


class UserSession(NasResource):
    """Represents an active logged-in user session."""

    @property
    def session_id(self) -> int:
        return self._raw.get("id", 0)

    @property
    def uid(self) -> int:
        return self._raw.get("uid", 0)

    @property
    def username(self) -> str:
        return self._raw.get("username", "")

    @property
    def client_ip(self) -> str:
        return self._raw.get("ip", "")

    @property
    def host(self) -> str:
        return self._raw.get("host", "")

    @property
    def login_time(self) -> int:
        return self._raw.get("login_time", 0)

    @property
    def is_current_connection(self) -> bool:
        return bool(self._raw.get("is_current_connection", False))

    @property
    def connection_duration_seconds(self) -> int:
        return self._raw.get("connection_duration", 0)

    def terminate(self) -> bool:
        """Terminate / disconnect this session."""
        return self._client.users.terminate_session(self.session_id)

    def __repr__(self) -> str:
        curr = " [current]" if self.is_current_connection else ""
        return f"<UserSession user='{self.username}' ip='{self.client_ip}' id={self.session_id}{curr}>"
