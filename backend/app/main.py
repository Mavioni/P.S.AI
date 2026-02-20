"""P.S.AI — Posthumous Social Artificial Intelligence

FastAPI application entry point. Wires up services, loads personas, exposes API.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import dialogue, health, personas
from app.core.config import settings
from app.services.database import Database
from app.services.dialogue_engine import DialogueEngine
from app.services.ollama_client import OllamaClient
from app.services.ontology_loader import OntologyLoader

# ── Shared service instances ────────────────────────────────────────

_ollama: OllamaClient | None = None
_ontology: OntologyLoader | None = None
_db: Database | None = None
_engine: DialogueEngine | None = None


def get_ollama() -> OllamaClient:
    assert _ollama is not None
    return _ollama


def get_ontology() -> OntologyLoader:
    assert _ontology is not None
    return _ontology


def get_db() -> Database:
    assert _db is not None
    return _db


def get_engine() -> DialogueEngine:
    assert _engine is not None
    return _engine


# ── Lifespan ────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _ollama, _ontology, _db, _engine

    # Start services
    _ollama = OllamaClient()
    _ontology = OntologyLoader(settings.ontology_path)
    _ontology.load_all()

    _db = Database(settings.db_path)
    await _db.connect()

    _engine = DialogueEngine(ollama=_ollama, ontology=_ontology, db=_db)

    persona_count = len(_ontology.list_all())
    print(f"[P.S.AI] Loaded {persona_count} personas from {settings.ontology_path}")
    print(f"[P.S.AI] Ollama endpoint: {settings.ollama_base_url}")
    print(f"[P.S.AI] Database: {settings.db_path}")

    yield

    # Shutdown
    await _ollama.close()
    await _db.close()


# ── App ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="P.S.AI",
    description=(
        "Posthumous Social Artificial Intelligence — "
        "Epistemic reconstruction of historical thinkers for structured philosophical dialogue."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(personas.router, prefix="/api")
app.include_router(dialogue.router, prefix="/api")
