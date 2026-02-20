"""Tests for the ItachiVault — encryption, decryption, and integrity."""

import pytest

from app.security.vault import ItachiVault


def test_encrypt_decrypt_roundtrip():
    """Encrypted data should decrypt to the original plaintext."""
    vault = ItachiVault("test-passphrase", "device-001")
    plaintext = b"The unexamined life is not worth living."

    encrypted = vault.encrypt_session(plaintext)
    decrypted = vault.decrypt_session(encrypted)

    assert decrypted == plaintext


def test_different_passphrases_fail():
    """Decryption with wrong passphrase should fail."""
    vault_a = ItachiVault("passphrase-a")
    vault_b = ItachiVault("passphrase-b")

    plaintext = b"Secret philosophical dialogue"
    encrypted = vault_a.encrypt_session(plaintext)

    with pytest.raises(Exception):
        vault_b.decrypt_session(encrypted)


def test_tampered_ciphertext_fails():
    """Tampering with ciphertext should be detected via HMAC."""
    vault = ItachiVault("test-passphrase")
    plaintext = b"Authentic content"

    encrypted = vault.encrypt_session(plaintext)

    # Tamper with ciphertext
    tampered_ct = bytearray(encrypted.ciphertext)
    tampered_ct[0] ^= 0xFF

    from app.security.vault import EncryptedPayload
    tampered = EncryptedPayload(
        ciphertext=bytes(tampered_ct),
        nonce=encrypted.nonce,
        salt=encrypted.salt,
        tag=encrypted.tag,
        hmac_digest=encrypted.hmac_digest,
    )

    with pytest.raises(ValueError, match="HMAC verification failed"):
        vault.decrypt_session(tampered)


def test_encrypted_payload_fields():
    """Verify encrypted payload has all required fields with correct sizes."""
    vault = ItachiVault("test")
    encrypted = vault.encrypt_session(b"data")

    assert len(encrypted.nonce) == 12   # AES-GCM nonce
    assert len(encrypted.salt) == 16    # Argon2id salt
    assert len(encrypted.tag) == 16     # GCM auth tag
    assert len(encrypted.hmac_digest) == 32  # SHA-256 HMAC
    assert len(encrypted.ciphertext) > 0
