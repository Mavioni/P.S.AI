"""Reward function for MCTS speaker selection.

Three-component reward as specified:
  1. Domain expertise  — does this persona have high domain relevance? (5.0x weight)
  2. Epistemic friction — does this persona disagree with the last speaker? (1.5x weight)
  3. Participation balance — penalize personas who have spoken too recently (-20s/turn)
"""

from __future__ import annotations

from app.orchestrator.state import ConversationState


# ── Weights ──────────────────────────────────────────────────────

DOMAIN_EXPERTISE_WEIGHT = 5.0
EPISTEMIC_FRICTION_WEIGHT = 1.5
RECENCY_PENALTY_PER_TURN = -0.2  # maps from -20s conceptual penalty to numeric score


def compute_reward(
    state: ConversationState,
    candidate_id: str,
    *,
    domain_scores: dict[str, float] | None = None,
    friction_matrix: dict[tuple[str, str], float] | None = None,
) -> float:
    """Compute the composite reward for selecting `candidate_id` as the next speaker.

    Args:
        state: Current conversation state.
        candidate_id: The persona being evaluated.
        domain_scores: {persona_id: relevance_score} for the current question topic.
            Scores in [0.0, 1.0]. Defaults to uniform 0.5 if not provided.
        friction_matrix: {(persona_a, persona_b): friction} measuring epistemic
            disagreement. Scores in [0.0, 1.0]. Defaults to 0.3 if not provided.

    Returns:
        Scalar reward value (higher = better candidate).
    """
    domain_scores = domain_scores or {}
    friction_matrix = friction_matrix or {}

    # 1. Domain expertise
    expertise = domain_scores.get(candidate_id, 0.5)
    domain_component = expertise * DOMAIN_EXPERTISE_WEIGHT

    # 2. Epistemic friction with last speaker
    friction_component = 0.0
    if state.last_speaker and state.last_speaker != candidate_id:
        pair = (candidate_id, state.last_speaker)
        reverse_pair = (state.last_speaker, candidate_id)
        friction = friction_matrix.get(pair, friction_matrix.get(reverse_pair, 0.3))
        friction_component = friction * EPISTEMIC_FRICTION_WEIGHT

    # 3. Participation balance (recency penalty)
    counts = state.speaker_counts
    candidate_count = counts.get(candidate_id, 0)
    avg_count = sum(counts.values()) / max(len(counts), 1)
    excess = candidate_count - avg_count
    balance_component = excess * RECENCY_PENALTY_PER_TURN

    return domain_component + friction_component + balance_component
