"""SQLite-backed persistence for dialogue sessions."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

import aiosqlite

from app.models.schemas import DialogueMode, SessionSummary

_SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    session_id   TEXT PRIMARY KEY,
    question     TEXT NOT NULL,
    mode         TEXT NOT NULL,
    persona_ids  TEXT NOT NULL,   -- JSON array
    created_at   TEXT NOT NULL,
    updated_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS turns (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id   TEXT NOT NULL REFERENCES sessions(session_id),
    turn_number  INTEGER NOT NULL,
    role         TEXT NOT NULL,
    persona_id   TEXT,
    persona_name TEXT,
    content      TEXT NOT NULL,
    created_at   TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_turns_session ON turns(session_id, turn_number);
"""


class Database:
    """Async SQLite wrapper for P.S.AI session and turn storage."""

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._conn: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = await aiosqlite.connect(str(self._db_path))
        self._conn.row_factory = aiosqlite.Row
        await self._conn.executescript(_SCHEMA)
        await self._conn.commit()

    async def close(self) -> None:
        if self._conn:
            await self._conn.close()

    # ── sessions ────────────────────────────────────────────────────

    async def create_session(
        self,
        question: str,
        mode: DialogueMode,
        persona_ids: list[str],
    ) -> str:
        session_id = uuid.uuid4().hex[:12]
        now = datetime.now(timezone.utc).isoformat()
        await self._conn.execute(
            "INSERT INTO sessions (session_id, question, mode, persona_ids, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (session_id, question, mode.value, json.dumps(persona_ids), now, now),
        )
        await self._conn.commit()
        return session_id

    async def get_session(self, session_id: str) -> dict | None:
        cursor = await self._conn.execute(
            "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
        )
        row = await cursor.fetchone()
        if not row:
            return None
        return dict(row)

    async def list_sessions(self, limit: int = 50) -> list[SessionSummary]:
        cursor = await self._conn.execute(
            "SELECT s.*, COUNT(t.id) as turn_count "
            "FROM sessions s LEFT JOIN turns t ON s.session_id = t.session_id "
            "GROUP BY s.session_id ORDER BY s.updated_at DESC LIMIT ?",
            (limit,),
        )
        rows = await cursor.fetchall()
        results = []
        for row in rows:
            r = dict(row)
            results.append(SessionSummary(
                session_id=r["session_id"],
                question=r["question"],
                mode=DialogueMode(r["mode"]),
                persona_ids=json.loads(r["persona_ids"]),
                turn_count=r["turn_count"],
                created_at=datetime.fromisoformat(r["created_at"]),
                updated_at=datetime.fromisoformat(r["updated_at"]),
            ))
        return results

    # ── turns ───────────────────────────────────────────────────────

    async def add_turn(
        self,
        session_id: str,
        turn_number: int,
        role: str,
        content: str,
        persona_id: str | None = None,
        persona_name: str | None = None,
    ) -> None:
        now = datetime.now(timezone.utc).isoformat()
        await self._conn.execute(
            "INSERT INTO turns (session_id, turn_number, role, persona_id, persona_name, content, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (session_id, turn_number, role, persona_id, persona_name, content, now),
        )
        await self._conn.execute(
            "UPDATE sessions SET updated_at = ? WHERE session_id = ?",
            (now, session_id),
        )
        await self._conn.commit()

    async def get_turns(self, session_id: str) -> list[dict]:
        cursor = await self._conn.execute(
            "SELECT * FROM turns WHERE session_id = ? ORDER BY turn_number",
            (session_id,),
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
