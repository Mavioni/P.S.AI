"""Tests for SecureMemory — zeroization and key lifecycle."""

from app.security.secure_memory import SecureMemory


def test_zeroize_clears_buffer():
    """After zeroization, all bytes should be zero."""
    buf = bytearray(b"sensitive key material here")
    SecureMemory.zeroize(buf)
    assert all(b == 0 for b in buf)


def test_secure_delete_clears_buffer():
    """After 3-pass secure delete, all bytes should be zero."""
    buf = bytearray(b"very sensitive data")
    SecureMemory.secure_delete(buf, passes=3)
    assert all(b == 0 for b in buf)


def test_scoped_key_zeroizes_on_exit():
    """Key material should be zeroed after exiting the context manager."""
    key_data = b"ephemeral-key-32-bytes-long-xxxx"

    with SecureMemory.scoped_key(key_data, max_lifetime_ms=5000) as key:
        assert len(key) == len(key_data)
        # Key is usable inside the context
        assert key == bytearray(key_data)

    # After exiting, key should be zeroed
    assert all(b == 0 for b in key)


def test_empty_buffer_handling():
    """Zeroize and secure_delete should handle empty buffers gracefully."""
    empty = bytearray(b"")
    SecureMemory.zeroize(empty)
    SecureMemory.secure_delete(empty)
    assert len(empty) == 0
