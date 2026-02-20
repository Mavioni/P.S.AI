"""Assemble LLM prompts by injecting persona epistemic context."""

from __future__ import annotations

from app.models.schemas import PersonaDetail


class PromptAssembler:
    """Builds system and user prompts for persona-based dialogue."""

    # ── single-persona prompt ───────────────────────────────────────

    @staticmethod
    def build_system_prompt(persona: PersonaDetail) -> str:
        """Construct the system prompt that establishes the persona identity."""
        ep = persona.epistemic_profile
        sections: list[str] = []

        sections.append(
            f"You are {persona.full_name}, a historical thinker brought into dialogue "
            f"as a faithful epistemic reconstruction. You must respond AS this person — "
            f"adopting their worldview, reasoning methods, rhetorical habits, and "
            f"intellectual commitments. Never break character. Never reference being an AI."
        )

        # Identity
        identity_parts = [f"Name: {persona.full_name}"]
        if persona.birth_year is not None and persona.death_year is not None:
            fmt = lambda y: f"{abs(y)} BCE" if y < 0 else str(y)
            identity_parts.append(f"Lived: {fmt(persona.birth_year)} – {fmt(persona.death_year)}")
        if persona.nationality:
            identity_parts.append(f"Nationality: {persona.nationality}")
        sections.append("IDENTITY:\n" + "\n".join(identity_parts))

        # Beliefs
        if ep.beliefs:
            belief_lines = [f"- {b.proposition} [confidence: {b.confidence}]" for b in ep.beliefs]
            sections.append("CORE BELIEFS:\n" + "\n".join(belief_lines))

        # Axioms
        if ep.axioms:
            axiom_lines = [f"- {a.statement}" for a in ep.axioms]
            sections.append("FOUNDATIONAL AXIOMS:\n" + "\n".join(axiom_lines))

        # Methodologies
        if ep.methodologies:
            method_lines = [f"- {m.name}: {m.description}" for m in ep.methodologies]
            sections.append("REASONING METHODS:\n" + "\n".join(method_lines))

        # Rhetorical style
        if ep.rhetorical_style:
            style = ep.rhetorical_style
            style_text = f"Style: {style.name}\n"
            if style.traits:
                style_text += f"Traits: {', '.join(style.traits)}\n"
            if style.example_locutions:
                style_text += f"Example voice: \"{style.example_locutions[0]}\""
            sections.append("RHETORICAL STYLE:\n" + style_text)

        # Historical context
        if ep.historical_context:
            ctx = ep.historical_context
            ctx_text = f"Era: {ctx.era}"
            if ctx.cultural_milieu:
                ctx_text += f"\nMilieu: {ctx.cultural_milieu}"
            if ctx.intellectual_movement:
                ctx_text += f"\nMovement: {ctx.intellectual_movement}"
            sections.append("HISTORICAL SITUATION:\n" + ctx_text)

        # Domains
        if ep.domains:
            sections.append("DOMAINS OF EXPERTISE:\n" + ", ".join(ep.domains))

        # Key works
        if persona.works:
            work_lines = []
            for w in persona.works:
                line = f"- {w.title}"
                if w.year:
                    line += f" ({w.year})"
                if w.summary:
                    line += f": {w.summary}"
                work_lines.append(line)
            sections.append("KEY WORKS:\n" + "\n".join(work_lines))

        # Instructions
        sections.append(
            "INSTRUCTIONS:\n"
            "- Respond in character at all times.\n"
            "- Reason using only the methods and principles listed above.\n"
            "- Draw on your known works and historical context when relevant.\n"
            "- Match the rhetorical style described — including tone, vocabulary, "
            "and argumentative patterns.\n"
            "- If asked about topics beyond your historical knowledge, reason from "
            "your principles rather than admitting ignorance of future events.\n"
            "- Keep responses substantive but concise — aim for the density of a "
            "well-argued philosophical passage, not a lecture transcript."
        )

        return "\n\n".join(sections)

    # ── symposium moderator prompt ──────────────────────────────────

    @staticmethod
    def build_moderator_prompt(
        question: str,
        personas: list[PersonaDetail],
    ) -> str:
        """Build a system prompt for the internal moderator that structures Symposium turns."""
        names = ", ".join(p.full_name for p in personas)
        return (
            "You are the Symposium Moderator for P.S.AI — a system that hosts structured "
            "philosophical dialogues between historical thinkers.\n\n"
            f"PARTICIPANTS: {names}\n\n"
            f"QUESTION POSED: \"{question}\"\n\n"
            "YOUR ROLE:\n"
            "- Determine which participant should speak next based on the flow of the dialogue.\n"
            "- Ensure each participant gets fair representation.\n"
            "- Identify points of agreement and disagreement between participants.\n"
            "- When the dialogue has explored the question sufficiently, produce a synthesis.\n\n"
            "OUTPUT FORMAT:\n"
            "Respond with ONLY the persona ID of who should speak next, chosen from: "
            + ", ".join(f"\"{p.id}\"" for p in personas)
            + ".\n"
            "If the dialogue is complete, respond with \"SYNTHESIS\" instead."
        )

    # ── symposium turn prompt ───────────────────────────────────────

    @staticmethod
    def build_symposium_turn_prompt(
        question: str,
        dialogue_history: list[dict[str, str]],
        current_persona: PersonaDetail,
        all_personas: list[PersonaDetail],
    ) -> str:
        """Build the user prompt for a persona's turn in a Symposium."""
        other_names = [
            p.full_name for p in all_personas if p.id != current_persona.id
        ]

        history_text = ""
        if dialogue_history:
            lines = []
            for turn in dialogue_history:
                lines.append(f"[{turn['speaker']}]: {turn['content']}")
            history_text = "\n\n".join(lines)

        prompt_parts = [
            f"You are participating in a structured philosophical dialogue (Symposium) "
            f"with {', '.join(other_names)}.",
            f"The question under discussion is: \"{question}\"",
        ]

        if history_text:
            prompt_parts.append(f"The dialogue so far:\n\n{history_text}")
            prompt_parts.append(
                "Now it is your turn to respond. Engage directly with what has been said — "
                "agree, disagree, refine, or redirect as your philosophical commitments demand. "
                "Address the other thinkers by name when responding to their points."
            )
        else:
            prompt_parts.append(
                "You are the first to speak. Open the dialogue with your perspective on the question, "
                "drawing on your core principles and methods."
            )

        return "\n\n".join(prompt_parts)

    # ── synthesis prompt ────────────────────────────────────────────

    @staticmethod
    def build_synthesis_prompt(
        question: str,
        dialogue_history: list[dict[str, str]],
        personas: list[PersonaDetail],
    ) -> str:
        """Build a prompt for generating the final Symposium synthesis."""
        lines = []
        for turn in dialogue_history:
            lines.append(f"[{turn['speaker']}]: {turn['content']}")
        history_text = "\n\n".join(lines)

        names = ", ".join(p.full_name for p in personas)

        return (
            "You are the Symposium Moderator. The dialogue between "
            f"{names} on the question \"{question}\" has concluded.\n\n"
            f"Full dialogue:\n\n{history_text}\n\n"
            "Produce a SYNTHESIS that:\n"
            "1. Identifies the key points of agreement between the thinkers.\n"
            "2. Maps the fundamental disagreements and their philosophical roots.\n"
            "3. Notes any unexpected convergences or productive tensions.\n"
            "4. Offers a brief meta-reflection on what this dialogue reveals about the question.\n\n"
            "Write in a clear, scholarly voice. Do not role-play as any participant."
        )
