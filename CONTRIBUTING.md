# Contributing to UGREEN NAS Python SDK

Thank you for your interest in contributing to the UGREEN NAS Python SDK!

## Development Guidelines

1. **Object-Oriented Design**:
   - Entities must be first-class domain classes extending `NasResource`.
   - Behavior methods (e.g. `user.edit()`, `disk.get_smart_info()`) belong on the domain instances.
   - Collections and factories belong on the Managers (`client.users`, `client.network`, etc.).
2. **Minimal Dependencies**:
   - The SDK relies only on the Python standard library (`urllib`, `json`) plus `cryptography` (or `pycryptodome`) for RSA PKCS#1 v1.5 encryption.
3. **Code Style & Typing**:
   - Use PEP 8 naming conventions (`snake_case` for methods and properties, `PascalCase` for classes).
   - Provide full type annotations (`from __future__ import annotations`).

## Running Checks & Tests

```bash
pip install -e .
pip install flake8
flake8 ugreen_nas --count --select=E9,F63,F7,F82 --show-source --statistics
python3 -m unittest discover
```

## Security

Please read [SECURITY.md](SECURITY.md) before submitting code dealing with authentication tokens or cryptographic handshakes.
