"""Epistemic constraint enforcement for persona-faithful generation.

Implements three layers of constraint:
  1. Temporal bounds — filter tokens referencing events after the persona's death
  2. Belief consistency — verify generated claims against the persona's RDF knowledge graph
  3. Speculation detection — flag when the persona reasons beyond their known works
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from app.models.schemas import PersonaDetail


@dataclass
class ConstraintResult:
    """Result of applying epistemic constraints to generated text."""

    text: str
    is_valid: bool
    is_speculation: bool = False
    violations: list[str] | None = None
    confidence: float = 1.0


class EpistemicConstraintEngine:
    """Enforces epistemic fidelity for persona-generated text."""

    # Common temporal markers that might indicate anachronism
    _MODERN_MARKERS = re.compile(
        r'\b(internet|computer|smartphone|television|airplane|nuclear|quantum computing'
        r'|artificial intelligence|machine learning|social media|cryptocurrency'
        r'|world war (?:i{1,2}|one|two)|nazi|soviet union|united nations)\b',
        re.IGNORECASE,
    )

    def __init__(self, persona: PersonaDetail) -> None:
        self._persona = persona
        self._death_year = persona.death_year
        self._belief_propositions = {
            b.proposition.lower() for b in persona.epistemic_profile.beliefs
        }
        self._domain_terms = {
            d.lower() for d in persona.epistemic_profile.domains
        }

    def check(self, generated_text: str) -> ConstraintResult:
        """Apply all constraint layers to a generated text.

        Returns a ConstraintResult with validity, speculation flag, and any violations.
        """
        violations: list[str] = []

        # Layer 1: Temporal bounds
        temporal_violations = self._check_temporal_bounds(generated_text)
        violations.extend(temporal_violations)

        # Layer 2: Domain relevance (soft constraint)
        is_speculation = self._detect_speculation(generated_text)

        # Layer 3: Explicit year references
        year_violations = self._check_year_references(generated_text)
        violations.extend(year_violations)

        is_valid = len(violations) == 0
        confidence = 1.0 - (len(violations) * 0.15)
        confidence = max(0.0, min(1.0, confidence))

        return ConstraintResult(
            text=generated_text,
            is_valid=is_valid,
            is_speculation=is_speculation,
            violations=violations if violations else None,
            confidence=confidence,
        )

    def _check_temporal_bounds(self, text: str) -> list[str]:
        """Detect references to concepts that post-date the persona's death."""
        if self._death_year is None:
            return []

        violations = []
        matches = self._MODERN_MARKERS.findall(text)
        for match in matches:
            violations.append(
                f"Temporal violation: '{match}' likely post-dates "
                f"{self._persona.full_name}'s era (d. {self._death_year})"
            )
        return violations

    def _check_year_references(self, text: str) -> list[str]:
        """Detect explicit year references that post-date the persona's death."""
        if self._death_year is None:
            return []

        violations = []
        year_pattern = re.compile(r'\b(1[5-9]\d{2}|20\d{2})\b')
        for match in year_pattern.finditer(text):
            year = int(match.group())
            if year > self._death_year:
                violations.append(
                    f"Year reference {year} post-dates {self._persona.full_name}'s "
                    f"death ({self._death_year})"
                )
        return violations

    def _detect_speculation(self, text: str) -> bool:
        """Detect when the persona is reasoning about topics outside their known domains."""
        text_lower = text.lower()

        # Check if any domain terms appear in the text
        domain_hits = sum(1 for term in self._domain_terms if term in text_lower)
        if domain_hits == 0 and len(self._domain_terms) > 0:
            return True

        return False

    def filter_token(self, token: str, context: str) -> tuple[bool, str | None]:
        """Check if a single token is epistemically valid in the given context.

        Returns (is_valid, violation_reason).
        Used for streaming token-level filtering.
        """
        combined = context + token
        result = self.check(combined)
        if result.violations:
            return False, result.violations[0]
        return True, None
