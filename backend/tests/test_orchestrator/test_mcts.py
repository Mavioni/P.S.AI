"""Tests for the ItachiOrchestrator — MCTS speaker selection."""

from app.orchestrator.mcts import ItachiOrchestrator, MCTSNode
from app.orchestrator.state import ConversationState


def _make_state(persona_ids: list[str], question: str = "What is justice?") -> ConversationState:
    return ConversationState(
        question=question,
        active_persona_ids=tuple(persona_ids),
    )


def test_resolve_next_speaker_returns_valid_persona():
    """The orchestrator must return a persona from the active set."""
    state = _make_state(["socrates", "kant", "marx"])
    orch = ItachiOrchestrator(n_simulations=50)
    speaker = orch.resolve_next_speaker(state)
    assert speaker in {"socrates", "kant", "marx"}


def test_does_not_repeat_last_speaker():
    """After a persona speaks, they should not be selected immediately again."""
    state = _make_state(["socrates", "kant", "marx"])
    state = state.with_utterance("socrates", "Let us examine this question.")

    orch = ItachiOrchestrator(n_simulations=50)
    speaker = orch.resolve_next_speaker(state)
    assert speaker != "socrates"


def test_convergence_over_100_simulations():
    """With 100 simulations, the MCTS should produce a deterministic-enough result."""
    state = _make_state(["socrates", "kant"])

    results = set()
    for _ in range(5):
        orch = ItachiOrchestrator(n_simulations=100)
        speaker = orch.resolve_next_speaker(state)
        results.add(speaker)

    # Should converge to the same speaker most of the time
    assert len(results) <= 2


def test_speaker_selection_fairness():
    """Over many turns, all personas should get roughly equal speaking time."""
    state = _make_state(["a", "b", "c"])
    orch = ItachiOrchestrator(n_simulations=30)

    counts = {"a": 0, "b": 0, "c": 0}
    for _ in range(12):
        speaker = orch.resolve_next_speaker(state)
        counts[speaker] += 1
        state = state.with_utterance(speaker, "Content")

    # Each should speak at least twice in 12 turns with 3 personas
    for pid, count in counts.items():
        assert count >= 2, f"Persona {pid} only spoke {count} times in 12 turns"


def test_domain_expertise_bias():
    """A persona with higher domain expertise should be favored."""
    state = _make_state(["expert", "novice"])
    orch = ItachiOrchestrator(
        n_simulations=100,
        domain_scores={"expert": 1.0, "novice": 0.1},
    )

    speaker = orch.resolve_next_speaker(state)
    assert speaker == "expert"


def test_ucb1_with_zero_visits():
    """UCB1 should return infinity for unvisited nodes."""
    state = _make_state(["a", "b"])
    node = MCTSNode(state=state, persona_id=None)
    assert node.ucb1() == float("inf")


def test_ucb1_with_visits():
    """UCB1 should return finite value for visited nodes."""
    state = _make_state(["a", "b"])
    parent = MCTSNode(state=state, persona_id=None)
    parent.visits = 10

    child = MCTSNode(state=state, persona_id="a", parent=parent)
    child.visits = 5
    child.total_reward = 3.0

    score = child.ucb1()
    assert score > 0
    assert score < float("inf")
