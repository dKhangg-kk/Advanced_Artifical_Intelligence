"""Cap 2 - Rule-based / Heuristic.

Thu tu uu tien (cong bo ro trong bao cao):
    1. Thang ngay neu co              (game.winning_moves(self))
    2. Chan doi thu thang ngay        (game.winning_moves(doi thu))
    3. Nuoc khong mo duong cho doi thu thang o luot sau
    4. Diem theo vi tri: cot giua > cot canh > cot bien, cong diem chuoi 2/3 quan
"""

from __future__ import annotations

from connect_four.agents.base import Agent
from connect_four.game.base import ConnectFourGame

# Trong so khoi tao - chinh lai sau khi tuning, luu vao configs/agents.yaml
DEFAULT_WEIGHTS: dict[str, float] = {
    "win": 10_000.0,
    "block": 9_000.0,
    "avoid_opponent_win": 5_000.0,
    "own_three": 100.0,
    "own_two": 10.0,
    "opponent_three": 80.0,
    "center_bonus": 6.0,
}


class HeuristicAgent(Agent):
    """Tac tu luat + ham diem. Xong khi: thang Random >= 95% tren 200 van."""

    name = "heuristic"
    level = 2

    def __init__(self, weights: dict[str, float] | None = None, seed: int | None = None) -> None:
        super().__init__(seed=seed)
        self.weights = dict(DEFAULT_WEIGHTS if weights is None else weights)

    def choose(self, game: ConnectFourGame) -> int:
        raise NotImplementedError("TODO: cai dat thu tu uu tien 1-4 o docstring")

    def score(self, game: ConnectFourGame) -> float:
        """Ham luong gia cho mot trang thai (dung lai trong Alpha-Beta)."""
        raise NotImplementedError("TODO: cong diem theo DEFAULT_WEIGHTS")
