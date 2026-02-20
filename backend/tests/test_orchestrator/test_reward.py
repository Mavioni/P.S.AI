"""Tests for the reward function components."""

from app.orchestrator.reward import compute_reward, DOMAIN_EXPERTISE_WEIGHT
from app.orchestrator.state import ConversationState


def _make_state(speakers_so_far: list[str]) -> ConversationState:
    all_ids = list(set(speakers_so_far) | {"a", "b", "c"})
    state = ConversationState(
        question="test",
        active_persona_ids=tuple(all_ids),
    )
    for s in speakers_so_far:
        state = state.with_utterance(s, "content")
    return state


def test_domain_expertise_weight():
    """Domain expertise should have 5.0x weight."""
    state = _make_state([])
    reward = compute_reward(
        state, "a", domain_scores={"a": 1.0}
    )
    assert reward >= DOMAIN_EXPERTISE_WEIGHT * 0.9


def test_friction_increases_reward():
    """High epistemic friction with last speaker should increase reward."""
    state = _make_state(["b"])
    reward_high_friction = compute_reward(
        state, "a", friction_matrix={("a", "b"): 0.9}
    )
    reward_low_friction = compute_reward(
        state, "a", friction_matrix={("a", "b"): 0.1}
    )
    assert reward_high_friction > reward_low_friction


def test_recency_penalty():
    """A persona who has spoken disproportionately should be penalized."""
    state = _make_state(["a", "b", "a", "b", "a"])
    # 'a' has spoken 3 times, 'b' 2 times, 'c' 0 times
    reward_a = compute_reward(state, "a")
    reward_c = compute_reward(state, "c")
    # 'c' should have higher reward due to participation balance
    assert reward_c > reward_a
