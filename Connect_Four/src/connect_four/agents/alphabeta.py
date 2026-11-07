"""Cap 3 - Minimax / Alpha-Beta.

Yeu cau cua de:
    - Negamax, gioi han do sau, dung ham luong gia cua HeuristicAgent.
    - Co co BAT/TAT cat tia de lam ablation A1 (so sanh so nut va thoi gian).
    - Co co BAT/TAT sap xep nuoc di (CENTER_FIRST) de do anh huong.
    - Dem so nut da duyet vao `last_stats.nodes`.

Xong khi: cung do sau <= 4, gia tri tra ve trung khop voi minimax thuan
(viet test trong tests/).
"""

from __future__ import annotations

from connect_four.agents.base import Agent, Budget
from connect_four.game.base import ConnectFourGame


class AlphaBetaAgent(Agent):
    """Tim kiem doi khang co cat tia."""

    name = "alphabeta"
    level = 3

    def __init__(
        self,
        budget: Budget | None = None,
        depth: int = 5,
        use_pruning: bool = True,
        use_ordering: bool = True,
        seed: int | None = None,
    ) -> None:
        super().__init__(budget=budget or Budget(depth=depth), seed=seed)
        self.depth = depth
        self.use_pruning = use_pruning
        self.use_ordering = use_ordering

    def choose(self, game: ConnectFourGame) -> int:
        raise NotImplementedError("TODO: negamax + alpha-beta, ghi last_stats")

    def negamax(self, game: ConnectFourGame, depth: int, alpha: float, beta: float) -> float:
        raise NotImplementedError("TODO: de quy negamax")
