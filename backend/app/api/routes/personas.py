"""Persona listing and detail endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.schemas import PersonaDetail, PersonaSummary

router = APIRouter(prefix="/personas", tags=["personas"])


@router.get("", response_model=list[PersonaSummary])
async def list_personas() -> list[PersonaSummary]:
    """Return all available personas (summary view)."""
    from app.main import get_ontology
    ontology = get_ontology()
    return [
        PersonaSummary(
            id=p.id,
            full_name=p.full_name,
            birth_year=p.birth_year,
            death_year=p.death_year,
            nationality=p.nationality,
            primary_language=p.primary_language,
            domains=p.domains,
            tagline=p.tagline,
        )
        for p in ontology.list_all()
    ]


@router.get("/{persona_id}", response_model=PersonaDetail)
async def get_persona(persona_id: str) -> PersonaDetail:
    """Return full persona detail including epistemic profile."""
    from app.main import get_ontology
    ontology = get_ontology()
    persona = ontology.get(persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail=f"Persona '{persona_id}' not found")
    return persona
