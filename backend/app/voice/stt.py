"""Speech-to-Text pipeline: audio capture → Silero VAD → Whisper → text.

Target latency: <300ms from end-of-utterance to transcript availability.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TranscriptionResult:
    """Result of STT processing."""

    text: str
    language: str = "en"
    confidence: float = 1.0
    latency_ms: float = 0.0


class STTPipeline:
    """Speech-to-text pipeline using faster-whisper with Silero VAD.

    Architecture:
      1. Audio arrives as 16-bit 24kHz mono PCM chunks
      2. Silero VAD detects voice activity boundaries
      3. Complete utterances are sent to faster-whisper (large-v3, int8)
      4. Greedy decoding produces transcription

    Note: Full implementation requires faster-whisper and silero-vad.
    This provides the interface and structure.
    """

    def __init__(
        self,
        model_size: str = "large-v3",
        compute_type: str = "int8",
        sample_rate: int = 24000,
    ) -> None:
        self._model_size = model_size
        self._compute_type = compute_type
        self._sample_rate = sample_rate
        self._model = None
        self._vad = None

    async def initialize(self) -> None:
        """Load Whisper model and VAD. Call once at startup."""
        try:
            from faster_whisper import WhisperModel
            self._model = WhisperModel(
                self._model_size,
                compute_type=self._compute_type,
            )
        except ImportError:
            pass  # Stub mode — voice features disabled

        try:
            import torch
            self._vad, _ = torch.hub.load(
                repo_or_dir="snakers4/silero-vad",
                model="silero_vad",
            )
        except (ImportError, Exception):
            pass

    async def transcribe(self, pcm_data: bytes) -> TranscriptionResult:
        """Transcribe a complete utterance from PCM audio data."""
        if self._model is None:
            return TranscriptionResult(
                text="[STT unavailable — faster-whisper not installed]",
                confidence=0.0,
            )

        import time
        import numpy as np

        start = time.monotonic()

        audio = np.frombuffer(pcm_data, dtype=np.int16).astype(np.float32) / 32768.0
        segments, info = self._model.transcribe(
            audio,
            beam_size=1,  # greedy decoding for speed
            language="en",
        )

        text_parts = [segment.text for segment in segments]
        text = " ".join(text_parts).strip()

        latency_ms = (time.monotonic() - start) * 1000

        return TranscriptionResult(
            text=text,
            language=info.language,
            confidence=1.0,
            latency_ms=latency_ms,
        )

    @property
    def available(self) -> bool:
        return self._model is not None
