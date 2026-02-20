"""ItachiOrchestrator — Monte Carlo Tree Search for persona turn resolution.

Uses UCB1 (Upper Confidence Bound) to balance exploration and exploitation
when deciding which historical thinker should speak next in a Symposium.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field

from app.orchestrator.reward import compute_reward
from app.orchestrator.state import ConversationState


@dataclass
class MCTSNode:
    """A node in the MCTS search tree.

    Each node represents a state after selecting a particular persona to speak.
    """

    state: ConversationState
    persona_id: str | None  # who spoke to arrive at this state (None for root)
    parent: MCTSNode | None = None
    children: list[MCTSNode] = field(default_factory=list)
    visits: int = 0
    total_reward: float = 0.0
    untried_actions: list[str] = field(default_factory=list)

    @property
    def avg_reward(self) -> float:
        return self.total_reward / self.visits if self.visits > 0 else 0.0

    def is_fully_expanded(self) -> bool:
        return len(self.untried_actions) == 0

    def is_terminal(self, max_depth: int) -> bool:
        return self.state.turn_number >= max_depth

    def ucb1(self, exploration_constant: float = 1.414) -> float:
        """Upper Confidence Bound for Trees."""
        if self.visits == 0:
            return float("inf")
        parent_visits = self.parent.visits if self.parent else self.visits
        exploitation = self.avg_reward
        exploration = exploration_constant * math.sqrt(
            math.log(parent_visits) / self.visits
        )
        return exploitation + exploration


class ItachiOrchestrator:
    """MCTS-based orchestrator for Symposium turn resolution.

    Given the current conversation state, runs N simulations to determine
    the optimal next speaker, balancing domain expertise, epistemic friction,
    and participation equity.
    """

    def __init__(
        self,
        *,
        n_simulations: int = 100,
        max_depth: int = 10,
        exploration_constant: float = 1.414,
        domain_scores: dict[str, float] | None = None,
        friction_matrix: dict[tuple[str, str], float] | None = None,
    ) -> None:
        self._n_simulations = n_simulations
        self._max_depth = max_depth
        self._exploration_constant = exploration_constant
        self._domain_scores = domain_scores or {}
        self._friction_matrix = friction_matrix or {}

    def resolve_next_speaker(self, state: ConversationState) -> str:
        """Run MCTS and return the persona_id of the best next speaker."""
        root = MCTSNode(
            state=state,
            persona_id=state.last_speaker,
            untried_actions=list(state.available_speakers()),
        )

        for _ in range(self._n_simulations):
            node = self._select(root)
            node = self._expand(node)
            reward = self._simulate(node)
            self._backpropagate(node, reward)

        # Choose the child with the most visits (robust selection)
        if not root.children:
            # Fallback: pick a random available speaker
            available = state.available_speakers()
            return random.choice(available) if available else state.active_persona_ids[0]

        best_child = max(root.children, key=lambda c: c.visits)
        assert best_child.persona_id is not None
        return best_child.persona_id

    # ── MCTS phases ─────────────────────────────────────────────

    def _select(self, node: MCTSNode) -> MCTSNode:
        """Descend the tree using UCB1 until we reach a node that is not fully expanded
        or is terminal."""
        while not node.is_terminal(self._max_depth):
            if not node.is_fully_expanded():
                return node
            if not node.children:
                return node
            node = max(
                node.children,
                key=lambda c: c.ucb1(self._exploration_constant),
            )
        return node

    def _expand(self, node: MCTSNode) -> MCTSNode:
        """Expand one untried action from the node."""
        if node.is_terminal(self._max_depth) or not node.untried_actions:
            return node

        action = node.untried_actions.pop(random.randrange(len(node.untried_actions)))

        # Create new state — in simulation we use empty content placeholder
        new_state = node.state.with_utterance(action, "[simulated]")

        child = MCTSNode(
            state=new_state,
            persona_id=action,
            parent=node,
            untried_actions=list(new_state.available_speakers()),
        )
        node.children.append(child)
        return child

    def _simulate(self, node: MCTSNode) -> float:
        """Run a random playout from the node to terminal depth, accumulating reward."""
        state = node.state
        total_reward = 0.0

        while state.turn_number < self._max_depth:
            available = state.available_speakers()
            if not available:
                break

            # Random rollout policy
            chosen = random.choice(available)
            total_reward += compute_reward(
                state,
                chosen,
                domain_scores=self._domain_scores,
                friction_matrix=self._friction_matrix,
            )
            state = state.with_utterance(chosen, "[simulated]")

        # Normalize by number of simulated turns
        turns_simulated = state.turn_number - node.state.turn_number
        return total_reward / max(turns_simulated, 1)

    def _backpropagate(self, node: MCTSNode, reward: float) -> None:
        """Propagate the simulation result up the tree."""
        current: MCTSNode | None = node
        while current is not None:
            current.visits += 1
            current.total_reward += reward
            current = current.parent
