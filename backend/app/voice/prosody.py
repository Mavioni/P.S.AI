"""Prosody engine: sentiment/intensity analysis → speech parameter adjustments.

Maps text emotional content to voice parameters:
  - Pitch variation
  - Speaking rate
  - Pause patterns
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ProsodyParams:
    """Computed prosody parameters for a text segment."""

    pitch_shift: float = 0.0      # semitones relative to base pitch
    rate_multiplier: float = 1.0   # 1.0 = normal, >1.0 = faster
    pause_before_ms: float = 0.0   # milliseconds of silence before segment
    emphasis: float = 0.5          # 0.0 = understated, 1.0 = highly emphatic


class ProsodyEngine:
    """Analyzes text to determine appropriate speech prosody.

    Uses keyword/pattern matching for sentiment and intensity analysis.
    For production, integrate a proper sentiment model.
    """

    # Patterns indicating heightened emphasis
    _EMPHASIS_MARKERS = {
        "!": 0.3,
        "?": 0.1,
        "MUST": 0.2,
        "NEVER": 0.2,
        "absolutely": 0.15,
        "certainly": 0.1,
        "impossible": 0.15,
    }

    _CONTEMPLATIVE_MARKERS = {
        "perhaps": -0.1,
        "maybe": -0.1,
        "consider": -0.05,
        "reflect": -0.1,
        "wonder": -0.1,
        "ponder": -0.15,
    }

    def analyze(self, text: str, base_variation: float = 0.5) -> ProsodyParams:
        """Compute prosody parameters for a text segment."""
        emphasis = 0.5

        # Check emphasis markers
        for marker, weight in self._EMPHASIS_MARKERS.items():
            if marker in text:
                emphasis += weight

        # Check contemplative markers
        for marker, weight in self._CONTEMPLATIVE_MARKERS.items():
            if marker.lower() in text.lower():
                emphasis += weight

        emphasis = max(0.0, min(1.0, emphasis))

        # Compute derived parameters
        pitch_shift = (emphasis - 0.5) * 4.0 * base_variation  # ±2 semitones
        rate_multiplier = 1.0 + (emphasis - 0.5) * 0.2 * base_variation

        # Add pause before weighty statements
        pause = 200.0 if emphasis > 0.7 else 0.0

        return ProsodyParams(
            pitch_shift=pitch_shift,
            rate_multiplier=rate_multiplier,
            pause_before_ms=pause,
            emphasis=emphasis,
        )
