"""File sharing and network services manager."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models.power import SshTerminal
from ..models.shares import FtpService, NfsService, RsyncService, SmbService, WebdavService

if TYPE_CHECKING:
    from ..client import UgreenNasClient


class ServicesManager:
    """Convenience access to network file sharing services and daemons."""

    def __init__(self, client: UgreenNasClient):
        self._client = client
        self.smb = SmbService(client)
        self.nfs = NfsService(client)
        self.ftp = FtpService(client)
        self.webdav = WebdavService(client)
        self.rsync = RsyncService(client)
        self.ssh = SshTerminal(client)
