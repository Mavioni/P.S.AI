"""Health check endpoint."""

from __future__ import annotations

from fastapi import APIRouter

from app.models.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    from app.main import get_ollama, get_ontology
    ollama = get_ollama()
    ontology = get_ontology()

    reachable = await ollama.is_reachable()
    return HealthResponse(
        status="ok",
        ollama_reachable=reachable,
        personas_loaded=len(ontology.list_all()),
    )
