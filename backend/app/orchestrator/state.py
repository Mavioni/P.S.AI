"""Conversation state representation for the MCTS orchestrator."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class UtteranceRecord:
    """Immutable record of a single utterance in the conversation."""

    persona_id: str
    content: str
    turn_number: int
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True)
class ConversationState:
    """Immutable snapshot of conversation state used as MCTS game state.

    Designed for value-based equality so identical states hash identically
    in the MCTS tree.
    """

    question: str
    active_persona_ids: tuple[str, ...]
    history: tuple[UtteranceRecord, ...] = ()
    turn_number: int = 0

    @property
    def last_speaker(self) -> str | None:
        return self.history[-1].persona_id if self.history else None

    @property
    def speaker_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {pid: 0 for pid in self.active_persona_ids}
        for record in self.history:
            counts[record.persona_id] = counts.get(record.persona_id, 0) + 1
        return counts

    def available_speakers(self) -> list[str]:
        """Return personas eligible to speak next (everyone except last speaker)."""
        return [
            pid for pid in self.active_persona_ids
            if pid != self.last_speaker
        ]

    def with_utterance(self, persona_id: str, content: str) -> ConversationState:
        """Return a new state with an appended utterance."""
        record = UtteranceRecord(
            persona_id=persona_id,
            content=content,
            turn_number=self.turn_number,
        )
        return ConversationState(
            question=self.question,
            active_persona_ids=self.active_persona_ids,
            history=self.history + (record,),
            turn_number=self.turn_number + 1,
        )
