"""Application configuration — all settings read from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Immutable runtime settings for the P.S.AI backend."""

    # Ollama
    ollama_base_url: str = field(
        default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    )
    ollama_model: str = field(
        default_factory=lambda: os.getenv("OLLAMA_MODEL", "llama3")
    )

    # Paths
    ontology_path: Path = field(
        default_factory=lambda: Path(os.getenv("PSAI_ONTOLOGY_PATH", str(Path(__file__).resolve().parents[3] / "ontology")))
    )
    db_path: Path = field(
        default_factory=lambda: Path(os.getenv("PSAI_DB_PATH", str(Path(__file__).resolve().parents[2] / "data" / "psai.db")))
    )

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = field(
        default_factory=lambda: os.getenv("PSAI_DEBUG", "false").lower() == "true"
    )

    # Symposium defaults
    max_turns: int = field(
        default_factory=lambda: int(os.getenv("PSAI_MAX_SYMPOSIUM_TURNS", "6"))
    )
    temperature: float = field(
        default_factory=lambda: float(os.getenv("PSAI_TEMPERATURE", "0.7"))
    )


settings = Settings()
