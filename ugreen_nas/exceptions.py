"""Exceptions for UGREEN NAS SDK."""


class UgreenNasError(Exception):
    """Base exception for all UGREEN NAS errors."""
    pass


class UgreenNasHttpError(UgreenNasError):
    """Raised when an HTTP transport error occurs."""

    def __init__(self, status_code: int, reason: str, body: str = ""):
        self.status_code = status_code
        self.reason = reason
        self.body = body
        super().__init__(f"HTTP {status_code}: {reason} - {body[:200]}")


class UgreenNasApiError(UgreenNasError):
    """Raised when the UGREEN NAS API returns an application-level error (code != 200)."""

    def __init__(self, code: int, message: str, raw: dict | None = None):
        self.code = code
        self.message = message
        self.raw = raw or {}
        super().__init__(f"UGOS API Error [{code}]: {message}")


class UgreenNasAuthError(UgreenNasApiError):
    """Raised when authentication fails or session expires."""
    pass
