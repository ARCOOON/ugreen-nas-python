# Security Policy

## Reporting Security Issues

If you discover a security vulnerability in this SDK or in how it interacts with UGREEN NAS hardware, please report it privately by contacting the project maintainers. Do not open public issues with sensitive vulnerability details or active token dumps.

## Credential Handling Best Practices

- **Never Hardcode Credentials**: Always use environment variables (`UGREEN_NAS_USER`, `UGREEN_NAS_PASSWORD`, `UGREEN_NAS_UGLINK`) in production code.
- **Relay URL Verification**: When using UGREENlink, the client performs a lookup via `https://api.ugnas.com`. Ensure TLS certificate validation is enabled in your environment.
- **Confirmation Passwords**: Endpoints performing irreversible destructive actions (such as user deletion) require current administrator password confirmation (`X-CurPass-Token`).
