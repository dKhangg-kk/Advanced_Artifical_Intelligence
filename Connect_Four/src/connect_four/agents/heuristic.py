"""Cap 2 - Rule-based / Heuristic.

Thu tu uu tien (cong bo ro trong bao cao):
    1. Thang ngay neu co              (game.winning_moves(self))
    2. Chan doi thu thang ngay        (game.winning_moves(doi thu))
    3. Nuoc khong mo duong cho doi thu thang o luot sau
    4. Diem theo vi tri: cot giua > cot canh > cot bien, cong diem chuoi 2/3 quan
"""

from __future__ import annotations

import random

from connect_four.agents.base import Agent, SearchStats
from connect_four.game.base import ConnectFourGame
from connect_four.game.constants import COLS, ROWS, WIN_LENGTH, other

_WINDOWS = tuple(
    tuple((r + dr * k, c + dc * k) for k in range(WIN_LENGTH))
    for dr, dc in ((0, 1), (1, 0), (1, 1), (-1, 1))
    for r in range(ROWS)
    for c in range(COLS)
    if 0 <= r + dr * (WIN_LENGTH - 1) < ROWS
    and 0 <= c + dc * (WIN_LENGTH - 1) < COLS
)

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
        self._rng = random.Random(seed)

    def choose(self, game: ConnectFourGame) -> int:
        """Thang > chan > an toan > diem; hoa diem chon theo seed.

        Chi thu nuoc tren ban sao. Nem ValueError neu khong con nuoc hop le.
        """
        legal = game.legal_actions()
        if not legal:
            raise ValueError("Khong con nuoc di hop le.")
        self.last_stats = SearchStats()
        player = game.current_player
        wins = game.winning_moves(player)
        if wins:
            self.last_stats.extra["eval_score"] = self.weights["win"]
            return self._rng.choice(wins)

        blocks = game.winning_moves(other(player))
        candidates = blocks or legal
        children = {action: game.clone_after(action) for action in candidates}
        safe = [action for action, child in children.items()
                if not child.winning_moves(other(player))]
        candidates = safe or candidates
        scores = {action: self.score(children[action], player) for action in candidates}
        best = max(scores.values())
        self.last_stats.nodes = len(children)
        self.last_stats.depth_reached = 1
        self.last_stats.extra["eval_score"] = best
        return self._rng.choice([action for action in candidates if scores[action] == best])

    def score(self, game: ConnectFourGame, player: int | None = None) -> float:
        """Diem tu goc nhin player (mac dinh current_player, dung cho negamax).

        Thang/thua: +/-win; hoa: 0. Cong diem cot gan giua, cua so 2/3
        quan khong bi chan va nuoc thang ngay; tru diem tuong ung cho doi thu.
        Khong sua game; player sai nem ValueError qua other().
        """
        player = game.current_player if player is None else player
        opponent = other(player)
        w = self.weights
        if game.is_terminal():
            return game.result(player) * w["win"]
        board = game.board.tolist()
        center = COLS // 2
        value = sum(
            (center - abs(c - center)) * w["center_bonus"]
            * ((board[r][c] == player) - (board[r][c] == opponent))
            for r in range(ROWS) for c in range(COLS)
        )
        for window in _WINDOWS:
            cells = [board[r][c] for r, c in window]
            mine, theirs = cells.count(player), cells.count(opponent)
            if theirs == 0:
                if mine == 3:
                    value += w["own_three"]
                elif mine == 2:
                    value += w["own_two"]
            elif mine == 0:
                if theirs == 3:
                    value -= w["opponent_three"]
                elif theirs == 2:
                    value -= w["own_two"]
        value += len(game.winning_moves(player)) * w["block"]
        value -= len(game.winning_moves(opponent)) * w["avoid_opponent_win"]
        return float(value)
