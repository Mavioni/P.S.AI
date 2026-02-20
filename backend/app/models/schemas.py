"""Pydantic schemas for API request / response models."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ── Enums ──────────────────────────────────────────────────────────

class DialogueMode(str, Enum):
    SINGLE = "single"
    SYMPOSIUM = "symposium"


class TurnRole(str, Enum):
    USER = "user"
    PERSONA = "persona"
    MODERATOR = "moderator"


# ── Persona ────────────────────────────────────────────────────────

class Belief(BaseModel):
    proposition: str
    confidence: float = Field(ge=0.0, le=1.0, default=0.9)


class Axiom(BaseModel):
    statement: str


class Methodology(BaseModel):
    name: str
    description: str


class RhetoricalStyle(BaseModel):
    name: str
    traits: list[str] = Field(default_factory=list)
    example_locutions: list[str] = Field(default_factory=list)


class HistoricalContext(BaseModel):
    era: str
    cultural_milieu: str = ""
    intellectual_movement: str = ""


class Work(BaseModel):
    title: str
    year: Optional[int] = None
    summary: str = ""


class EpistemicProfile(BaseModel):
    beliefs: list[Belief] = Field(default_factory=list)
    axioms: list[Axiom] = Field(default_factory=list)
    methodologies: list[Methodology] = Field(default_factory=list)
    rhetorical_style: Optional[RhetoricalStyle] = None
    historical_context: Optional[HistoricalContext] = None
    domains: list[str] = Field(default_factory=list)


class PersonaSummary(BaseModel):
    id: str
    full_name: str
    birth_year: Optional[int] = None
    death_year: Optional[int] = None
    nationality: str = ""
    primary_language: str = ""
    domains: list[str] = Field(default_factory=list)
    tagline: str = ""


class PersonaDetail(PersonaSummary):
    epistemic_profile: EpistemicProfile
    works: list[Work] = Field(default_factory=list)


# ── Dialogue ───────────────────────────────────────────────────────

class DialogueTurn(BaseModel):
    role: TurnRole
    persona_id: Optional[str] = None
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StartDialogueRequest(BaseModel):
    question: str = Field(..., min_length=1)
    persona_ids: list[str] = Field(..., min_length=1)
    mode: DialogueMode = DialogueMode.SINGLE
    max_turns: Optional[int] = None


class DialogueTurnResponse(BaseModel):
    turn_number: int
    role: TurnRole
    persona_id: Optional[str] = None
    persona_name: Optional[str] = None
    content: str


class DialogueResponse(BaseModel):
    session_id: str
    question: str
    mode: DialogueMode
    turns: list[DialogueTurnResponse] = Field(default_factory=list)
    is_complete: bool = False


class ContinueDialogueRequest(BaseModel):
    user_input: Optional[str] = None


# ── Session ────────────────────────────────────────────────────────

class SessionSummary(BaseModel):
    session_id: str
    question: str
    mode: DialogueMode
    persona_ids: list[str]
    turn_count: int
    created_at: datetime
    updated_at: datetime


# ── Health ─────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str = "ok"
    ollama_reachable: bool = False
    personas_loaded: int = 0
