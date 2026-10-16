"""Core HTTP client and session management for UGREEN NAS."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
import urllib.error
from typing import Any

from .crypto import rsa_encrypt_pkcs1_v15
from .exceptions import UgreenNasApiError, UgreenNasAuthError, UgreenNasHttpError

UGREENLINK_LOOKUP_URL = "https://api.ugnas.com/api/p2p/v2/ta/nodeInfo/byAlias"


class UgreenNasClient:
    """Synchronous client for UGREEN NAS UGOS Pro APIs."""

    def __init__(
        self,
        base_url: str | None = None,
        uglink_id: str | None = None,
        timeout: float = 30.0,
    ):
        """Initialize UGREEN NAS client.

        Args:
            base_url: Direct URL to the NAS (e.g. https://192.168.1.100 or https://nas.local)
            uglink_id: UGREENlink ID or alias (e.g. "xxx" or "https://ug.link/xxx")
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.token: str | None = None
        self.token_id: str | None = None
        self.session_public_key: str | None = None
        self.login_info: dict[str, Any] = {}

        if uglink_id:
            self.base_url = self.resolve_uglink_id(uglink_id)
        elif base_url:
            self.base_url = self._normalize_url(base_url)
        else:
            raise ValueError("Either base_url or uglink_id must be provided.")

        # OOP Resource Managers
        from .managers import (
            GroupManager,
            NetworkManager,
            PowerManager,
            ServicesManager,
            ShareManager,
            StorageManager,
            UserManager,
        )

        self.users = UserManager(self)
        self.groups = GroupManager(self)
        self.network = NetworkManager(self)
        self.storage = StorageManager(self)
        self.shares = ShareManager(self)
        self.services = ServicesManager(self)
        self.power = PowerManager(self)

    @classmethod
    def resolve_uglink_id(cls, uglink_ref: str, timeout: float = 10.0) -> str:
        """Resolve a UGREENlink ID (or ug.link URL) to the direct HTTPS relay domain URL."""
        alias = uglink_ref.strip()
        # Extract alias from URL if needed
        if "://" in alias:
            parsed = urllib.parse.urlparse(alias)
            # e.g. https://ug.link/xxx -> path is /xxx
            path_parts = parsed.path.strip("/").split("/")
            if path_parts and path_parts[0]:
                alias = path_parts[0]
            elif parsed.netloc:
                alias = parsed.netloc.split(".")[0]

        req = urllib.request.Request(
            UGREENLINK_LOOKUP_URL,
            data=json.dumps({"alias": alias}).encode("utf-8"),
            headers={"Content-Type": "application/json", "User-Agent": "UgreenNasSdk/1.0"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            raise UgreenNasHttpError(0, f"Failed to reach UGREENlink lookup service: {e}")

        if body.get("code") != 200:
            raise UgreenNasApiError(
                body.get("code", 0),
                f"UGREENlink lookup failed for '{alias}': {body.get('msg')}",
                body,
            )

        data = body.get("data", {})
        relay_domain = data.get("relayDomain")
        if not relay_domain:
            raise UgreenNasApiError(0, "UGREENlink node info did not return relayDomain", body)

        return f"https://{alias}.{relay_domain}"

    @staticmethod
    def _normalize_url(url: str) -> str:
        url = url.strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            url = f"https://{url}"
        return url.rstrip("/")

    def get_rsa_public_key(self, username: str) -> str:
        """Fetch RSA public key token for password encryption."""
        url = f"{self.base_url}/ugreen/v1/verify/check"
        payload = json.dumps({"username": username}).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                headers = dict(resp.headers)
                rsa_token = headers.get("X-Rsa-Token") or headers.get("x-rsa-token")
                if not rsa_token:
                    raise UgreenNasAuthError(0, "Server response missing X-Rsa-Token header")
                return rsa_token
        except urllib.error.HTTPError as e:
            raise UgreenNasHttpError(e.code, e.reason, e.read().decode("utf-8", "ignore"))

    def login(self, username: str, password: str, keepalive: bool = True) -> dict[str, Any]:
        """Authenticate with username and password, establishing a session.

        Encrypts password using RSA PKCS#1 v1.5 with the server public key.
        """
        rsa_token = self.get_rsa_public_key(username)
        encrypted_pw = rsa_encrypt_pkcs1_v15(password, rsa_token)

        login_payload = {
            "username": username,
            "password": encrypted_pw,
            "otp": True,
            "keepalive": keepalive,
            "is_simple": True,
        }
        res = self.request("POST", "/ugreen/v1/verify/login", json_data=login_payload, authenticated=False)
        data = res.get("data", {})
        self.token = data.get("token")
        self.token_id = data.get("token_id")
        self.session_public_key = data.get("public_key")
        self.login_info = data
        return data

    def is_logged_in(self) -> bool:
        """Check if current session is active and valid."""
        if not self.token:
            return False
        try:
            res = self.request("GET", "/ugreen/v1/verify/is_login")
            return res.get("code") == 200
        except Exception:
            return False

    def heartbeat(self) -> dict[str, Any]:
        """Send keepalive heartbeat."""
        return self.request("GET", "/ugreen/v1/verify/heartbeat")

    def get_system_info(self) -> dict[str, Any]:
        """Get common hardware and system details."""
        return self.request("GET", "/ugreen/v1/sysinfo/machine/common").get("data", {})

    def get_system_stats(self) -> dict[str, Any]:
        """Get real-time CPU, RAM, network, and disk metrics."""
        return self.request("GET", "/ugreen/v1/taskmgr/stat/get_all").get("data", {})

    def request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        authenticated: bool = True,
    ) -> dict[str, Any]:
        """Execute an HTTP request against the NAS."""
        req_headers = {"Content-Type": "application/json", "User-Agent": "UgreenNasSdk/1.0"}
        if headers:
            req_headers.update(headers)

        query_params = dict(params or {})

        if authenticated:
            if not self.token:
                raise UgreenNasAuthError(0, "Not authenticated. Call login() first.")

            # Both URL query token and encrypted header tokens are supported across UGOS versions
            query_params["token"] = self.token
            req_headers["X-Ugreen-Token"] = self.token

            if self.token_id and self.session_public_key:
                try:
                    enc_token = rsa_encrypt_pkcs1_v15(self.token, self.session_public_key)
                    req_headers["x-ugreen-security-key"] = self.token_id
                    req_headers["x-ugreen-token"] = enc_token
                except Exception:
                    pass

        url = f"{self.base_url}/{path.lstrip('/')}"
        if query_params:
            url = f"{url}?{urllib.parse.urlencode(query_params)}"

        req_body = json.dumps(json_data).encode("utf-8") if json_data is not None else None
        req = urllib.request.Request(url, data=req_body, headers=req_headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                resp_text = resp.read().decode("utf-8")
                try:
                    body = json.loads(resp_text)
                except Exception:
                    return {"code": resp.status, "raw": resp_text}

                code = body.get("code")
                if code is not None and code != 200:
                    raise UgreenNasApiError(code, body.get("msg", "API error"), body)
                return body
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", "ignore")
            raise UgreenNasHttpError(e.code, e.reason, err_body)
        except urllib.error.URLError as e:
            raise UgreenNasHttpError(0, str(e.reason))
