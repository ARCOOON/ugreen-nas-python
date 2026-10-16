"""Base resource model for UGREEN NAS OOP entities."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..client import UgreenNasClient


class NasResource:
    """Base class for domain resources associated with a client connection."""

    def __init__(self, client: UgreenNasClient, data: dict[str, Any]):
        self._client = client
        self._raw = data

    @property
    def raw(self) -> dict[str, Any]:
        """Return the raw JSON dictionary from the NAS API."""
        return self._raw

    def _refresh(self, new_data: dict[str, Any]) -> None:
        """Update internal dictionary."""
        self._raw.update(new_data)

    def to_dict(self) -> dict[str, Any]:
        """Convert object to standard dictionary."""
        return dict(self._raw)
