"""WebSocket protocol — serialize/deserialize packets with integrity checks.

Provides HMAC-SHA256 checksums, nonce tracking, timestamp validation,
and replay prevention for the binary protobuf-framed WebSocket protocol.
"""

from __future__ import annotations

import hashlib
import hmac
import time
from collections import OrderedDict


class ProtocolHandler:
    """Manages WebSocket packet integrity and replay prevention.

    Note: Full protobuf integration requires compiled stubs from psai.proto.
    This implementation works with JSON-serialized packets as a compatible
    intermediate format until protobuf compilation is set up.
    """

    # Nonce window: reject nonces older than this many seconds
    _NONCE_WINDOW_SECONDS = 300  # 5 minutes
    _MAX_NONCE_CACHE = 10000

    def __init__(self, shared_secret: bytes) -> None:
        self._secret = shared_secret
        # OrderedDict for LRU-style nonce tracking
        self._seen_nonces: OrderedDict[str, float] = OrderedDict()

    def compute_hmac(self, payload: bytes) -> bytes:
        """Compute HMAC-SHA256 over a serialized payload."""
        return hmac.new(self._secret, payload, hashlib.sha256).digest()

    def verify_hmac(self, payload: bytes, expected_hmac: bytes) -> bool:
        """Verify HMAC using constant-time comparison."""
        computed = self.compute_hmac(payload)
        return hmac.compare_digest(computed, expected_hmac)

    def validate_timestamp(self, timestamp_ms: int) -> bool:
        """Reject packets with timestamps outside the nonce window."""
        now_ms = int(time.time() * 1000)
        diff_seconds = abs(now_ms - timestamp_ms) / 1000
        return diff_seconds <= self._NONCE_WINDOW_SECONDS

    def check_replay(self, nonce: str) -> bool:
        """Return True if nonce is fresh (not a replay). False if replayed."""
        if nonce in self._seen_nonces:
            return False

        # Evict old nonces
        now = time.time()
        while self._seen_nonces:
            oldest_nonce, oldest_time = next(iter(self._seen_nonces.items()))
            if now - oldest_time > self._NONCE_WINDOW_SECONDS:
                self._seen_nonces.pop(oldest_nonce)
            else:
                break

        # Cap cache size
        while len(self._seen_nonces) >= self._MAX_NONCE_CACHE:
            self._seen_nonces.popitem(last=False)

        self._seen_nonces[nonce] = now
        return True

    def validate_packet(
        self,
        payload: bytes,
        nonce: str,
        timestamp_ms: int,
        packet_hmac: bytes,
    ) -> tuple[bool, str]:
        """Full packet validation: HMAC + timestamp + replay check.

        Returns (is_valid, error_message).
        """
        if not self.verify_hmac(payload, packet_hmac):
            return False, "HMAC verification failed"

        if not self.validate_timestamp(timestamp_ms):
            return False, "Timestamp outside acceptable window"

        if not self.check_replay(nonce):
            return False, "Nonce replay detected"

        return True, ""
