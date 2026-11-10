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

from time import perf_counter

from connect_four.agents.base import Agent, Budget, SearchStats
from connect_four.agents.heuristic import HeuristicAgent
from connect_four.game.base import ConnectFourGame
from connect_four.game.constants import CENTER_FIRST


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
        self.depth = self.budget.depth if self.budget.depth is not None else depth
        if self.depth < 1:
            raise ValueError("Do sau phai >= 1.")
        self.use_pruning = use_pruning
        self.use_ordering = use_ordering
        self._heuristic = HeuristicAgent()

    def choose(self, game: ConnectFourGame) -> int:
        """Chon cot tot nhat theo do sau, khong sua game; het nuoc nem ValueError."""
        legal = game.legal_actions()
        if not legal:
            raise ValueError("Khong con nuoc di hop le.")
        start = perf_counter()
        self.last_stats = SearchStats(nodes=1)
        actions = [c for c in CENTER_FIRST if c in legal] if self.use_ordering else legal
        best_action = actions[0]
        best_score = alpha = -float("inf")
        for action in actions:
            score = -self._negamax(game.clone_after(action), self.depth - 1,
                                   -float("inf"), -alpha, game.current_player, -1)
            if score > best_score:
                best_score, best_action = score, action
            if self.use_pruning:
                alpha = max(alpha, score)
        self.last_stats.extra["eval_score"] = best_score
        self.last_stats.depth_reached = self.depth
        self.last_stats.time_ms = (perf_counter() - start) * 1000
        return best_action

    def negamax(self, game: ConnectFourGame, depth: int, alpha: float, beta: float) -> float:
        """Tra diem theo nguoi dang di o goc voi cua so alpha/beta, khong sua game."""
        return self._negamax(game, depth, alpha, beta, game.current_player, 1)

    def _negamax(self, game: ConnectFourGame, depth: int, alpha: float, beta: float,
                 root_player: int, color: int) -> float:
        self.last_stats.nodes += 1
        if depth <= 0 or game.is_terminal():
            # Heuristic khong doi xung: giu goc nhin goc, chi doi dau bang color.
            return color * self._heuristic.score(game, root_player)
        legal = game.legal_actions()
        actions = [c for c in CENTER_FIRST if c in legal] if self.use_ordering else legal
        best = -float("inf")
        for action in actions:
            score = -self._negamax(game.clone_after(action), depth - 1, -beta, -alpha,
                                   root_player, -color)
            best = max(best, score)
            if self.use_pruning:
                alpha = max(alpha, score)
                if alpha >= beta:
                    break
        return best
