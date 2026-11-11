"""Cap 4 - MCTS voi UCT.

Bon buoc: chon (UCT) -> mo rong -> mo phong (rollout) -> cap nhat.
Ngan sach: Budget.simulations hoac Budget.time_s.

Xong khi: thang Random >= 95% o 500 mo phong. Khao sat ngan sach
100 / 500 / 1000 / 2000 / 5000 mo phong de lam ablation A2.
"""

from __future__ import annotations

import math
import random
import time

from connect_four.agents.base import Agent
from connect_four.game.base import ConnectFourGame


class MCTSNode:
    """Mot nut trong cay tim kiem (N = so lan tham, W = tong phan thuong)."""

    __slots__ = ("parent", "action", "children", "visits", "wins", "untried")

    def __init__(self, parent: "MCTSNode | None" = None, action: int | None = None) -> None:
        self.parent = parent
        self.action = action
        self.children: dict[int, "MCTSNode"] = {}
        self.visits = 0
        self.wins = 0.0
        self.untried: list[int] = []


class MCTSAgent(Agent):
    """Monte Carlo Tree Search, chon nuoc bang UCT."""

    name = "mcts"
    level = 4

    def __init__(self, simulations: int = 1000, c: float = 1.414, seed: int | None = None, budget=None) -> None:
        from connect_four.agents.base import Budget

        super().__init__(budget=budget or Budget(simulations=simulations), seed=seed)
        self.c = c
        self._rng = random.Random(seed)

    def choose(self, game: ConnectFourGame) -> int:
        legal = game.legal_actions()
        if not legal:
            raise ValueError("Khong con nuoc di hop le.")
        root_player = game.current_player
        root = MCTSNode()
        root.untried = legal[:]
        deadline = time.perf_counter() + self.budget.time_s if self.budget.time_s else None
        limit = self.budget.simulations or simulations_default(self.budget)
        simulations = 0

        while simulations < limit and (deadline is None or time.perf_counter() < deadline):
            state = game.clone()
            node = root
            while not node.untried and node.children and not state.is_terminal():
                action, node = self._select_child(node, state.current_player == root_player)
                state.step(action)
            if node.untried and not state.is_terminal():
                action = self._rng.choice(node.untried)
                node.untried.remove(action)
                state.step(action)
                child = MCTSNode(parent=node, action=action)
                child.untried = state.legal_actions()
                node.children[action] = child
                node = child
            while not state.is_terminal():
                state.step(self._rng.choice(state.legal_actions()))
            reward = state.result(root_player)
            while node is not None:
                node.visits += 1
                node.wins += reward
                node = node.parent
            simulations += 1

        best = max(legal, key=lambda action: (root.children.get(action, MCTSNode()).visits, self._rng.random()))
        self.last_stats.nodes = len(root.children)
        self.last_stats.simulations = simulations
        self.last_stats.depth_reached = 0
        return best

    def _select_child(self, node: MCTSNode, maximizing: bool) -> tuple[int, MCTSNode]:
        log_parent = math.log(max(1, node.visits))
        def uct(item: tuple[int, MCTSNode]) -> float:
            action, child = item
            mean = child.wins / child.visits if child.visits else 0.0
            explore = self.c * math.sqrt(log_parent / child.visits) if child.visits else float("inf")
            return (mean if maximizing else -mean) + explore
        return max(node.children.items(), key=uct)


def simulations_default(budget) -> int:
    """Fallback for a time-only budget; the loop is then stopped by deadline."""
    return 10**9
