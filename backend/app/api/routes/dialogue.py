"""Dialogue endpoints — start single or Symposium sessions, continue, retrieve."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    ContinueDialogueRequest,
    DialogueMode,
    DialogueResponse,
    DialogueTurnResponse,
    SessionSummary,
    StartDialogueRequest,
    TurnRole,
)

router = APIRouter(prefix="/dialogue", tags=["dialogue"])


@router.post("", response_model=DialogueResponse)
async def start_dialogue(req: StartDialogueRequest) -> DialogueResponse:
    """Start a new dialogue session (single or Symposium)."""
    from app.main import get_engine
    engine = get_engine()

    try:
        if req.mode == DialogueMode.SINGLE:
            if len(req.persona_ids) != 1:
                raise HTTPException(
                    status_code=400,
                    detail="Single mode requires exactly one persona_id",
                )
            return await engine.start_single(req.question, req.persona_ids[0])

        elif req.mode == DialogueMode.SYMPOSIUM:
            if len(req.persona_ids) < 2:
                raise HTTPException(
                    status_code=400,
                    detail="Symposium mode requires at least two persona_ids",
                )
            max_turns = req.max_turns or 6
            return await engine.start_symposium(req.question, req.persona_ids, max_turns)

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{session_id}/continue", response_model=DialogueResponse)
async def continue_dialogue(
    session_id: str,
    req: ContinueDialogueRequest,
) -> DialogueResponse:
    """Continue an existing single-persona dialogue with new user input."""
    from app.main import get_engine
    engine = get_engine()

    if not req.user_input:
        raise HTTPException(status_code=400, detail="user_input is required")

    try:
        return await engine.continue_single(session_id, req.user_input)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{session_id}", response_model=DialogueResponse)
async def get_dialogue(session_id: str) -> DialogueResponse:
    """Retrieve a dialogue session with all its turns."""
    from app.main import get_db
    db = get_db()

    session = await db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")

    import json
    turns_raw = await db.get_turns(session_id)
    turns = [
        DialogueTurnResponse(
            turn_number=t["turn_number"],
            role=TurnRole(t["role"]),
            persona_id=t.get("persona_id"),
            persona_name=t.get("persona_name"),
            content=t["content"],
        )
        for t in turns_raw
    ]

    return DialogueResponse(
        session_id=session_id,
        question=session["question"],
        mode=DialogueMode(session["mode"]),
        turns=turns,
        is_complete=True,
    )


@router.get("", response_model=list[SessionSummary])
async def list_sessions() -> list[SessionSummary]:
    """List recent dialogue sessions."""
    from app.main import get_db
    db = get_db()
    return await db.list_sessions()
