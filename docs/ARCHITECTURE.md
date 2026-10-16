# Architecture & Protocol Specification

This document details the internal architecture, authentication handshake, relay resolution, and reverse-engineered protocol mechanics for **UGREEN NAS UGOS Pro** in the Python SDK.

---

## 1. Overview

UGOS Pro exposes a unified JSON REST API over HTTPS on port 9443 (direct) or through UGREENlink relay tunnels (remote). The NAS backend is organized around modular subsystems (`ctlmgr`, `filemgr`, `sysinfo`, `desktop`, `network`, `storage`, `terminal`).

```
+-------------------------------------------------------------+
|                     UgreenNasClient                         |
+-------------------------------------------------------------+
   |             |             |             |            |
   v             v             v             v            v
UserManager NetworkManager StorageManager ShareManager PowerManager
   |             |             |             |            |
   +-------------+-------------+-------------+------------+
                               |
                               v
                     HTTP Transport Layer
             (Direct IP or UGREENlink Relay Domain)
```

---

## 2. Remote Connectivity: UGREENlink Relay

When connecting to the NAS outside of local LAN without a direct public IP, UGOS devices connect to UGREEN's global P2P/relay infrastructure.

### Relay Lookup Endpoint

- **URL:** `POST https://api.ugnas.com/api/p2p/v2/ta/nodeInfo/byAlias`
- **Headers:** `Content-Type: application/json`, `User-Agent: Mozilla/5.0...` (Required to bypass Cloudflare protection)
- **Request Body:**
  ```json
  {
    "alias": "my-nas-alias"
  }
  ```
- **Response:**
  ```json
  {
    "code": 200,
    "msg": "SUCCESS",
    "data": {
      "alias": "my-nas-alias",
      "relayDomain": "relay01.ug.link",
      "appDomain": "relay01.ugapp.link",
      "dockerDomain": "relay01.ugdocker.link",
      "netInfo": {
        "ipv4": ["192.168.1.100"],
        "httpPort": 9999,
        "httpsPort": 9443
      }
    }
  }
  ```

### Direct Relay URL Construction

`UgreenNasClient.resolve_uglink_id` constructs the target HTTPS URL as:
```
https://{alias}.{relayDomain}
# Example: https://my-nas-alias.relay01.ug.link
```

---

## 3. Cryptographic Handshake & Authentication

UGOS Pro uses asymmetric RSA encryption to protect credentials over the wire.

### Phase 1: Public Key Discovery
1. The client issues a verification check for the target username:
   - **URL:** `POST /ugreen/v1/verify/check`
   - **Body:** `{"username": "my-user"}`
2. The server responds with an HTTP header containing an RSA public key token:
   - Header: `X-Rsa-Token: -----BEGIN RSA PUBLIC KEY-----\n...`
   
> **SPKI Anomaly Note:** While UGOS labels the PEM as `BEGIN RSA PUBLIC KEY` (PKCS#1), the ASN.1 payload actually contains SubjectPublicKeyInfo (SPKI, PKCS#8). In `ugreen_nas/crypto.py`, the header is normalized to `BEGIN PUBLIC KEY` before loading with `cryptography.hazmat.primitives.serialization.load_pem_public_key`.

### Phase 2: Password Encryption & Login
1. Password is encrypted using RSA PKCS#1 v1.5 padding:
   ```python
   encrypted_password = rsa_encrypt_pkcs1_v15(password, rsa_token)
   ```
2. The client submits credentials:
   - **URL:** `POST /ugreen/v1/verify/login`
   - **Body:**
     ```json
     {
       "username": "my-user",
       "password": "<base64_encrypted_pw>",
       "otp": true,
       "keepalive": true,
       "is_simple": true
     }
     ```
3. The server responds with session tokens:
   - `token`: Bearer authentication token
   - `token_id`: Security key identifier
   - `public_key`: Session encryption public key

### Phase 3: Authenticated Request Security
Subsequent API calls must pass:
1. URL query parameter: `?token=<token>`
2. Header: `X-Ugreen-Token: <token>`
3. Header: `x-ugreen-security-key: <token_id>`
4. Header: `x-ugreen-token: <rsa_encrypted_token_with_session_public_key>`

### Phase 4: Sensitive / Destructive Actions (Confirmation Password)
Endpoints performing irreversible actions (e.g. `DELETE /ugreen/v1/user/delete`) require current administrator password confirmation passed in the header:
```
X-CurPass-Token: RSA_Encrypt(current_admin_password, server_public_key)
```

---

## 4. Domain Resource Model

The Python SDK structures APIs into stateful domain models (`NasResource`) rather than flat procedural calls:

- **Entity Independence**: Each model (`User`, `NetworkInterface`, `Disk`, `Volume`, `SharedFolder`) maintains a reference to the active `client` and its current `raw` dictionary.
- **Active Behavior**: Changing state calls `.edit()`, `.delete()`, `.set_static_ip()`, or `.get_smart_info()` directly on the resource instance and refreshes its underlying state.
- **Lazy Evaluation**: Sub-managers (e.g., `client.network.interfaces`, `client.storage.disks`) return collections of domain models ready for interaction.
