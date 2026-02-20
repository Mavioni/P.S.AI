"""Load persona profiles from JSON-LD files in the ontology directory."""

from __future__ import annotations

import json
from pathlib import Path

from app.models.schemas import (
    Axiom,
    Belief,
    EpistemicProfile,
    HistoricalContext,
    Methodology,
    PersonaDetail,
    RhetoricalStyle,
    Work,
)


class OntologyLoader:
    """Reads JSON-LD persona files and hydrates them into Pydantic models."""

    def __init__(self, ontology_root: Path) -> None:
        self._root = ontology_root
        self._personas: dict[str, PersonaDetail] = {}

    # ── public ──────────────────────────────────────────────────────

    def load_all(self) -> dict[str, PersonaDetail]:
        """Scan the personas/ directory and load every .jsonld file."""
        persona_dir = self._root / "personas"
        if not persona_dir.is_dir():
            return self._personas

        for path in sorted(persona_dir.glob("*.jsonld")):
            persona = self._load_file(path)
            if persona:
                self._personas[persona.id] = persona

        return self._personas

    def get(self, persona_id: str) -> PersonaDetail | None:
        return self._personas.get(persona_id)

    def list_all(self) -> list[PersonaDetail]:
        return list(self._personas.values())

    # ── internals ───────────────────────────────────────────────────

    def _load_file(self, path: Path) -> PersonaDetail | None:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None

        persona_id = path.stem  # filename without extension

        profile_raw = raw.get("psai:hasEpistemicProfile", {})

        beliefs = [
            Belief(
                proposition=b.get("psai:proposition", ""),
                confidence=float(b.get("psai:confidence", 0.9)),
            )
            for b in _as_list(profile_raw.get("psai:holdsBelief", []))
        ]

        axioms = [
            Axiom(statement=a.get("psai:axiomStatement", ""))
            for a in _as_list(profile_raw.get("psai:acceptsAxiom", []))
        ]

        methodologies = [
            Methodology(
                name=m.get("psai:methodName", ""),
                description=m.get("psai:methodDescription", ""),
            )
            for m in _as_list(profile_raw.get("psai:employsMethodology", []))
        ]

        style_raw = profile_raw.get("psai:exhibitsStyle")
        rhetorical_style = None
        if style_raw:
            traits_raw = style_raw.get("psai:styleTraits", "")
            traits = [t.strip() for t in traits_raw.split(",")] if isinstance(traits_raw, str) else traits_raw
            locutions_raw = style_raw.get("psai:exampleLocution", "")
            locutions = [locutions_raw] if isinstance(locutions_raw, str) else locutions_raw
            rhetorical_style = RhetoricalStyle(
                name=style_raw.get("psai:styleName", ""),
                traits=traits,
                example_locutions=locutions,
            )

        ctx_raw = profile_raw.get("psai:situatedIn")
        historical_context = None
        if ctx_raw:
            historical_context = HistoricalContext(
                era=ctx_raw.get("psai:era", ""),
                cultural_milieu=ctx_raw.get("psai:culturalMilieu", ""),
                intellectual_movement=ctx_raw.get("psai:intellectualMovement", ""),
            )

        domains_raw = profile_raw.get("psai:engagesDomain", [])
        domains = domains_raw if isinstance(domains_raw, list) else [domains_raw]

        works = [
            Work(
                title=w.get("psai:workTitle", ""),
                year=w.get("psai:workYear"),
                summary=w.get("psai:workSummary", ""),
            )
            for w in _as_list(raw.get("psai:authoredWork", []))
        ]

        epistemic_profile = EpistemicProfile(
            beliefs=beliefs,
            axioms=axioms,
            methodologies=methodologies,
            rhetorical_style=rhetorical_style,
            historical_context=historical_context,
            domains=domains,
        )

        return PersonaDetail(
            id=persona_id,
            full_name=raw.get("psai:fullName", persona_id),
            birth_year=raw.get("psai:birthYear"),
            death_year=raw.get("psai:deathYear"),
            nationality=raw.get("psai:nationality", ""),
            primary_language=raw.get("psai:primaryLanguage", ""),
            domains=domains,
            tagline=_make_tagline(raw),
            epistemic_profile=epistemic_profile,
            works=works,
        )


# ── helpers ─────────────────────────────────────────────────────────

def _as_list(val: object) -> list:
    if isinstance(val, list):
        return val
    if val:
        return [val]
    return []


def _make_tagline(raw: dict) -> str:
    name = raw.get("psai:fullName", "")
    birth = raw.get("psai:birthYear")
    death = raw.get("psai:deathYear")
    if birth is not None and death is not None:
        fmt = lambda y: f"{abs(y)} BCE" if y < 0 else str(y)
        return f"{name} ({fmt(birth)} – {fmt(death)})"
    return name
