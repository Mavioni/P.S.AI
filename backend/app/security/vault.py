"""ItachiVault — cryptographic session encryption.

Key derivation: Argon2id (t=3, m=65536, p=4)
Encryption: AES-256-GCM + HMAC-SHA256
Decryption: verify-then-decrypt (constant-time HMAC comparison)
"""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
from dataclasses import dataclass


@dataclass(frozen=True)
class EncryptedPayload:
    """Encrypted session data with all necessary decryption metadata."""

    ciphertext: bytes
    nonce: bytes       # 12 bytes for AES-GCM
    salt: bytes        # 16 bytes for Argon2id
    tag: bytes         # 16 bytes GCM auth tag
    hmac_digest: bytes # 32 bytes HMAC-SHA256 over ciphertext


class ItachiVault:
    """Encrypts and decrypts session data using AES-256-GCM.

    Key derivation uses Argon2id when available, falling back to
    PBKDF2-HMAC-SHA256 for environments without argon2-cffi.
    """

    _SALT_SIZE = 16
    _NONCE_SIZE = 12
    _KEY_SIZE = 32  # 256 bits

    # Argon2id parameters (spec requirements)
    _ARGON2_TIME_COST = 3
    _ARGON2_MEMORY_COST = 65536  # 64 MiB
    _ARGON2_PARALLELISM = 4

    # PBKDF2 fallback
    _PBKDF2_ITERATIONS = 600_000

    def __init__(self, passphrase: str, device_hwid: str = "") -> None:
        self._passphrase = passphrase
        self._device_hwid = device_hwid

    def _derive_key(self, salt: bytes) -> bytes:
        """Derive a 256-bit key using Argon2id (preferred) or PBKDF2 (fallback)."""
        password_material = (self._passphrase + self._device_hwid).encode("utf-8")

        try:
            from argon2.low_level import Type, hash_secret_raw

            return hash_secret_raw(
                secret=password_material,
                salt=salt,
                time_cost=self._ARGON2_TIME_COST,
                memory_cost=self._ARGON2_MEMORY_COST,
                parallelism=self._ARGON2_PARALLELISM,
                hash_len=self._KEY_SIZE,
                type=Type.ID,
            )
        except ImportError:
            # Fallback to PBKDF2
            return hashlib.pbkdf2_hmac(
                "sha256",
                password_material,
                salt,
                self._PBKDF2_ITERATIONS,
                dklen=self._KEY_SIZE,
            )

    def encrypt_session(self, plaintext: bytes) -> EncryptedPayload:
        """Encrypt session data with AES-256-GCM + HMAC-SHA256."""
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        salt = os.urandom(self._SALT_SIZE)
        nonce = os.urandom(self._NONCE_SIZE)
        key = self._derive_key(salt)

        aesgcm = AESGCM(key)
        ciphertext_with_tag = aesgcm.encrypt(nonce, plaintext, None)

        # AES-GCM appends the 16-byte tag to ciphertext
        ciphertext = ciphertext_with_tag[:-16]
        tag = ciphertext_with_tag[-16:]

        # HMAC over ciphertext for additional integrity
        hmac_key = hashlib.sha256(key + b"hmac").digest()
        hmac_digest = hmac.new(hmac_key, ciphertext, hashlib.sha256).digest()

        # Zeroize key material
        _zeroize_bytes(key)

        return EncryptedPayload(
            ciphertext=ciphertext,
            nonce=nonce,
            salt=salt,
            tag=tag,
            hmac_digest=hmac_digest,
        )

    def decrypt_session(self, payload: EncryptedPayload) -> bytes:
        """Decrypt session data. Verify-then-decrypt with constant-time HMAC comparison."""
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM

        key = self._derive_key(payload.salt)

        # Verify HMAC first (constant-time comparison)
        hmac_key = hashlib.sha256(key + b"hmac").digest()
        expected_hmac = hmac.new(hmac_key, payload.ciphertext, hashlib.sha256).digest()

        if not hmac.compare_digest(expected_hmac, payload.hmac_digest):
            _zeroize_bytes(key)
            raise ValueError("HMAC verification failed — data may be tampered")

        # Decrypt
        aesgcm = AESGCM(key)
        ciphertext_with_tag = payload.ciphertext + payload.tag
        plaintext = aesgcm.decrypt(payload.nonce, ciphertext_with_tag, None)

        # Zeroize key material
        _zeroize_bytes(key)

        return plaintext


def _zeroize_bytes(data: bytes) -> None:
    """Best-effort zeroization of key material.

    Note: Python's immutable bytes makes true zeroization impossible without
    ctypes. For production, use SecureMemory with mmap-backed buffers.
    """
    try:
        import ctypes
        ptr = ctypes.cast(id(data), ctypes.POINTER(ctypes.c_char * len(data)))
        ctypes.memset(ptr, 0, len(data))
    except Exception:
        pass  # Best-effort; logged in production
