"""Core dialogue engine — handles single-persona and Symposium interactions.

Symposium mode uses the ItachiOrchestrator (MCTS) for intelligent speaker
selection rather than simple round-robin.
"""

from __future__ import annotations

from app.models.schemas import (
    DialogueMode,
    DialogueResponse,
    DialogueTurnResponse,
    PersonaDetail,
    TurnRole,
)
from app.orchestrator.mcts import ItachiOrchestrator
from app.orchestrator.state import ConversationState
from app.services.database import Database
from app.services.ollama_client import OllamaClient
from app.services.ontology_loader import OntologyLoader
from app.services.prompt_assembler import PromptAssembler


class DialogueEngine:
    """Orchestrates single-persona dialogue and Symposium multi-agent dialogue."""

    def __init__(
        self,
        ollama: OllamaClient,
        ontology: OntologyLoader,
        db: Database,
        *,
        domain_scores: dict[str, float] | None = None,
        friction_matrix: dict[tuple[str, str], float] | None = None,
    ) -> None:
        self._ollama = ollama
        self._ontology = ontology
        self._db = db
        self._assembler = PromptAssembler()
        self._domain_scores = domain_scores or {}
        self._friction_matrix = friction_matrix or {}

    # ── single persona dialogue ─────────────────────────────────────

    async def start_single(
        self,
        question: str,
        persona_id: str,
    ) -> DialogueResponse:
        """Start a dialogue with a single persona."""
        persona = self._ontology.get(persona_id)
        if not persona:
            raise ValueError(f"Unknown persona: {persona_id}")

        session_id = await self._db.create_session(
            question=question,
            mode=DialogueMode.SINGLE,
            persona_ids=[persona_id],
        )

        # Record the user's question
        await self._db.add_turn(session_id, 0, TurnRole.USER.value, question)

        # Generate persona response
        system_prompt = self._assembler.build_system_prompt(persona)
        response_text = await self._ollama.generate(question, system=system_prompt)

        await self._db.add_turn(
            session_id, 1, TurnRole.PERSONA.value, response_text,
            persona_id=persona_id, persona_name=persona.full_name,
        )

        return DialogueResponse(
            session_id=session_id,
            question=question,
            mode=DialogueMode.SINGLE,
            turns=[
                DialogueTurnResponse(
                    turn_number=0, role=TurnRole.USER, content=question,
                ),
                DialogueTurnResponse(
                    turn_number=1,
                    role=TurnRole.PERSONA,
                    persona_id=persona_id,
                    persona_name=persona.full_name,
                    content=response_text,
                ),
            ],
            is_complete=False,
        )

    async def continue_single(
        self,
        session_id: str,
        user_input: str,
    ) -> DialogueResponse:
        """Continue an existing single-persona dialogue."""
        session = await self._db.get_session(session_id)
        if not session:
            raise ValueError(f"Session not found: {session_id}")

        import json
        persona_ids = json.loads(session["persona_ids"])
        persona = self._ontology.get(persona_ids[0])
        if not persona:
            raise ValueError(f"Persona not found: {persona_ids[0]}")

        turns = await self._db.get_turns(session_id)
        next_turn = len(turns)

        # Record user input
        await self._db.add_turn(session_id, next_turn, TurnRole.USER.value, user_input)

        # Build chat history for context
        messages = [{"role": "system", "content": self._assembler.build_system_prompt(persona)}]
        for t in turns:
            role = "user" if t["role"] == TurnRole.USER.value else "assistant"
            messages.append({"role": role, "content": t["content"]})
        messages.append({"role": "user", "content": user_input})

        response_text = await self._ollama.chat(messages)

        await self._db.add_turn(
            session_id, next_turn + 1, TurnRole.PERSONA.value, response_text,
            persona_id=persona.id, persona_name=persona.full_name,
        )

        # Build full turn list
        all_turns = await self._db.get_turns(session_id)
        turn_responses = [
            DialogueTurnResponse(
                turn_number=t["turn_number"],
                role=TurnRole(t["role"]),
                persona_id=t.get("persona_id"),
                persona_name=t.get("persona_name"),
                content=t["content"],
            )
            for t in all_turns
        ]

        return DialogueResponse(
            session_id=session_id,
            question=session["question"],
            mode=DialogueMode.SINGLE,
            turns=turn_responses,
            is_complete=False,
        )

    # ── symposium (multi-persona) ───────────────────────────────────

    async def start_symposium(
        self,
        question: str,
        persona_ids: list[str],
        max_turns: int = 6,
    ) -> DialogueResponse:
        """Run a full Symposium: multiple personas discuss a question in structured rounds."""
        personas: list[PersonaDetail] = []
        for pid in persona_ids:
            p = self._ontology.get(pid)
            if not p:
                raise ValueError(f"Unknown persona: {pid}")
            personas.append(p)

        session_id = await self._db.create_session(
            question=question,
            mode=DialogueMode.SYMPOSIUM,
            persona_ids=persona_ids,
        )

        # Record the question
        await self._db.add_turn(session_id, 0, TurnRole.USER.value, question)

        dialogue_history: list[dict[str, str]] = []
        turn_responses: list[DialogueTurnResponse] = [
            DialogueTurnResponse(turn_number=0, role=TurnRole.USER, content=question),
        ]

        # Initialize MCTS orchestrator for intelligent speaker selection
        orchestrator = ItachiOrchestrator(
            n_simulations=100,
            max_depth=max_turns,
            domain_scores=self._domain_scores,
            friction_matrix=self._friction_matrix,
        )

        conv_state = ConversationState(
            question=question,
            active_persona_ids=tuple(persona_ids),
        )

        turn_number = 1

        for _round_idx in range(max_turns):
            # MCTS selects the next speaker based on domain expertise,
            # epistemic friction, and participation balance
            speaker_id = orchestrator.resolve_next_speaker(conv_state)
            speaker = next(p for p in personas if p.id == speaker_id)

            # Build persona-specific system prompt
            system_prompt = self._assembler.build_system_prompt(speaker)

            # Build the turn prompt with dialogue context
            turn_prompt = self._assembler.build_symposium_turn_prompt(
                question=question,
                dialogue_history=dialogue_history,
                current_persona=speaker,
                all_personas=personas,
            )

            # Generate response
            response_text = await self._ollama.generate(turn_prompt, system=system_prompt)

            # Record and update MCTS conversation state
            dialogue_history.append({
                "speaker": speaker.full_name,
                "persona_id": speaker.id,
                "content": response_text,
            })
            conv_state = conv_state.with_utterance(speaker.id, response_text)

            await self._db.add_turn(
                session_id, turn_number, TurnRole.PERSONA.value, response_text,
                persona_id=speaker.id, persona_name=speaker.full_name,
            )

            turn_responses.append(DialogueTurnResponse(
                turn_number=turn_number,
                role=TurnRole.PERSONA,
                persona_id=speaker.id,
                persona_name=speaker.full_name,
                content=response_text,
            ))

            turn_number += 1

        # Generate synthesis
        synthesis_prompt = self._assembler.build_synthesis_prompt(
            question, dialogue_history, personas,
        )
        synthesis = await self._ollama.generate(
            synthesis_prompt,
            system="You are a scholarly moderator synthesizing a philosophical dialogue.",
        )

        await self._db.add_turn(
            session_id, turn_number, TurnRole.MODERATOR.value, synthesis,
        )

        turn_responses.append(DialogueTurnResponse(
            turn_number=turn_number,
            role=TurnRole.MODERATOR,
            persona_name="Symposium Moderator",
            content=synthesis,
        ))

        return DialogueResponse(
            session_id=session_id,
            question=question,
            mode=DialogueMode.SYMPOSIUM,
            turns=turn_responses,
            is_complete=True,
        )
