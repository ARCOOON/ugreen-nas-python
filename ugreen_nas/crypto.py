"""Crypto helpers for UGREEN NAS authentication (RSA PKCS#1 v1.5)."""

import base64


def rsa_encrypt_pkcs1_v15(plaintext: str | bytes, pem_base64: str) -> str:
    """Encrypt plaintext using RSA PKCS#1 v1.5 padding with the base64-encoded PEM public key.

    Returns the encrypted ciphertext as a base64 string.
    """
    if isinstance(plaintext, str):
        plaintext = plaintext.encode("utf-8")

    # decode outer base64 to obtain PEM bytes
    try:
        pem_bytes = base64.b64decode(pem_base64)
    except Exception:
        pem_bytes = pem_base64.encode("utf-8") if isinstance(pem_base64, str) else pem_base64

    # Try cryptography library first
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import padding

        pub_key = serialization.load_pem_public_key(pem_bytes)
        cipher_bytes = pub_key.encrypt(plaintext, padding.PKCS1v15())
        return base64.b64encode(cipher_bytes).decode("ascii")
    except ImportError:
        pass

    # Fallback to PyCryptodome if cryptography is not installed
    try:
        from Crypto.Cipher import PKCS1_v1_5
        from Crypto.PublicKey import RSA

        rsa_key = RSA.import_key(pem_bytes)
        cipher = PKCS1_v1_5.new(rsa_key)
        cipher_bytes = cipher.encrypt(plaintext)
        return base64.b64encode(cipher_bytes).decode("ascii")
    except ImportError:
        raise ImportError(
            "Neither 'cryptography' nor 'pycryptodome' is installed. "
            "Please install cryptography: pip install cryptography"
        )
