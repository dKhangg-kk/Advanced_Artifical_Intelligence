"""Cap 4 - MCTS voi UCT.

Bon buoc: chon (UCT) -> mo rong -> mo phong (rollout) -> cap nhat.
Ngan sach: Budget.simulations hoac Budget.time_s.

Xong khi: thang Random >= 95% o 500 mo phong. Khao sat ngan sach
100 / 500 / 1000 / 2000 / 5000 mo phong de lam ablation A2.
"""

from __future__ import annotations

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

    def __init__(self, simulations: int = 1000, c: float = 1.414, seed: int | None = None) -> None:
        from connect_four.agents.base import Budget

        super().__init__(budget=Budget(simulations=simulations), seed=seed)
        self.c = c

    def choose(self, game: ConnectFourGame) -> int:
        raise NotImplementedError("TODO: vong lap MCTS + UCT, ghi last_stats.simulations")
