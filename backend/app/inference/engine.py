"""ItachiInferenceEngine — local LLM inference via Ollama with epistemic constraints.

Wraps the Ollama client with:
  - Persona-contextualized system prompts
  - Token-level epistemic constraint enforcement
  - Streaming generation with speculation detection
  - Model integrity verification (SHA-256)
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import AsyncIterator

from app.inference.epistemic_constraints import ConstraintResult, EpistemicConstraintEngine
from app.models.schemas import PersonaDetail
from app.services.ollama_client import OllamaClient
from app.services.prompt_assembler import PromptAssembler


@dataclass
class GenerationResult:
    """Result of a constrained persona generation."""

    text: str
    persona_id: str
    is_speculation: bool = False
    confidence: float = 1.0
    violations: list[str] | None = None


class ItachiInferenceEngine:
    """LLM inference with epistemic guardrails.

    Coordinates between:
      - OllamaClient (raw LLM generation)
      - PromptAssembler (persona context injection)
      - EpistemicConstraintEngine (post-generation validation)
    """

    def __init__(self, ollama: OllamaClient) -> None:
        self._ollama = ollama
        self._assembler = PromptAssembler()

    async def generate_persona_response(
        self,
        persona: PersonaDetail,
        prompt: str,
        *,
        temperature: float | None = None,
    ) -> GenerationResult:
        """Generate a persona response with epistemic constraint checking."""
        system_prompt = self._assembler.build_system_prompt(persona)
        constraint_engine = EpistemicConstraintEngine(persona)

        # Generate
        response = await self._ollama.generate(
            prompt,
            system=system_prompt,
            temperature=temperature,
        )

        # Validate
        result = constraint_engine.check(response)

        return GenerationResult(
            text=response,
            persona_id=persona.id,
            is_speculation=result.is_speculation,
            confidence=result.confidence,
            violations=result.violations,
        )

    async def generate_persona_stream(
        self,
        persona: PersonaDetail,
        prompt: str,
        *,
        temperature: float | None = None,
    ) -> AsyncIterator[str]:
        """Streaming generation with per-token epistemic filtering."""
        system_prompt = self._assembler.build_system_prompt(persona)
        constraint_engine = EpistemicConstraintEngine(persona)

        context_buffer = ""

        async for token in self._ollama.generate_stream(
            prompt,
            system=system_prompt,
            temperature=temperature,
        ):
            is_valid, violation = constraint_engine.filter_token(token, context_buffer)

            if is_valid:
                context_buffer += token
                yield token
            else:
                # Skip invalid tokens silently — the constraint engine
                # has already logged the violation
                context_buffer += token  # still track for context

    @staticmethod
    def verify_model_integrity(model_path: Path, expected_sha256: str) -> bool:
        """Verify model file integrity via SHA-256 checksum.

        Should be called before loading any model weights.
        """
        if not model_path.exists():
            return False

        sha256 = hashlib.sha256()
        with open(model_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)

        return sha256.hexdigest() == expected_sha256.lower()
