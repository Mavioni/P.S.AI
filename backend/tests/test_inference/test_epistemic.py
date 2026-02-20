"""Tests for epistemic constraint enforcement."""

from app.inference.epistemic_constraints import EpistemicConstraintEngine
from app.models.schemas import (
    Belief,
    EpistemicProfile,
    HistoricalContext,
    PersonaDetail,
)


def _make_persona(
    name: str = "Nikola Tesla",
    death_year: int = 1943,
    domains: list[str] | None = None,
) -> PersonaDetail:
    return PersonaDetail(
        id="tesla",
        full_name=name,
        birth_year=1856,
        death_year=death_year,
        domains=domains or ["Electrical Engineering", "Physics"],
        epistemic_profile=EpistemicProfile(
            beliefs=[
                Belief(proposition="Alternating current is superior.", confidence=0.95),
            ],
            domains=domains or ["Electrical Engineering", "Physics"],
            historical_context=HistoricalContext(era="19th-20th century"),
        ),
    )


def test_temporal_violation_detected():
    """References to post-death concepts should be flagged."""
    engine = EpistemicConstraintEngine(_make_persona(death_year=1943))
    result = engine.check(
        "The internet has revolutionized communication worldwide."
    )
    assert not result.is_valid
    assert result.violations
    assert any("internet" in v.lower() for v in result.violations)


def test_year_violation_detected():
    """Explicit year references post-death should be flagged."""
    engine = EpistemicConstraintEngine(_make_persona(death_year=1943))
    result = engine.check("By the year 2020, technology had advanced greatly.")
    assert not result.is_valid
    assert any("2020" in v for v in result.violations)


def test_valid_text_passes():
    """Text within the persona's era should pass."""
    engine = EpistemicConstraintEngine(_make_persona(death_year=1943))
    result = engine.check(
        "Alternating current will prove superior to direct current in every measure."
    )
    assert result.is_valid
    assert result.violations is None


def test_speculation_detection():
    """Text outside the persona's domains should be flagged as speculation."""
    engine = EpistemicConstraintEngine(
        _make_persona(domains=["Electrical Engineering"])
    )
    result = engine.check(
        "The political dynamics of medieval feudalism reveal interesting patterns."
    )
    assert result.is_speculation


def test_token_level_filtering():
    """Per-token filtering should detect violations incrementally."""
    engine = EpistemicConstraintEngine(_make_persona(death_year=1943))
    is_valid, _ = engine.filter_token("internet", "The ")
    assert not is_valid
