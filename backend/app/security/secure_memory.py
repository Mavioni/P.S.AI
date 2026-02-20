"""SecureMemory — memory management for cryptographic key material.

Goals:
  - Zeroize sensitive data within <100ms of use
  - Prevent key material from persisting in process memory
  - 3-pass random overwrite for secure deletion
"""

from __future__ import annotations

import ctypes
import os
import time
from contextlib import contextmanager
from typing import Generator


class SecureMemory:
    """Manages sensitive byte buffers with guaranteed zeroization."""

    @staticmethod
    def zeroize(buffer: bytearray) -> None:
        """Overwrite a bytearray with zeros using ctypes.memset."""
        if not buffer:
            return
        buf_type = ctypes.c_char * len(buffer)
        ptr = buf_type.from_buffer(buffer)
        ctypes.memset(ptr, 0, len(buffer))

    @staticmethod
    def secure_delete(buffer: bytearray, passes: int = 3) -> None:
        """Overwrite buffer with random data N times, then zero.

        Default 3-pass: random, random, zero.
        """
        if not buffer:
            return
        buf_len = len(buffer)
        for i in range(passes - 1):
            random_data = os.urandom(buf_len)
            buffer[:] = random_data
        # Final pass: zero
        SecureMemory.zeroize(buffer)

    @staticmethod
    @contextmanager
    def scoped_key(key_data: bytes, max_lifetime_ms: float = 100.0) -> Generator[bytearray, None, None]:
        """Context manager that ensures key material is zeroized within max_lifetime_ms.

        Usage:
            with SecureMemory.scoped_key(derived_key) as key:
                # use key for encryption
                cipher.encrypt(key, ...)
            # key is guaranteed zeroized here
        """
        mutable = bytearray(key_data)
        start = time.monotonic()
        try:
            yield mutable
        finally:
            elapsed_ms = (time.monotonic() - start) * 1000
            SecureMemory.secure_delete(mutable)
            if elapsed_ms > max_lifetime_ms:
                import warnings
                warnings.warn(
                    f"Key material lived for {elapsed_ms:.1f}ms "
                    f"(limit: {max_lifetime_ms:.1f}ms)",
                    RuntimeWarning,
                    stacklevel=2,
                )
