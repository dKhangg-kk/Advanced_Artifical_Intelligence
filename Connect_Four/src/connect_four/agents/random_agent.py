"""Cap 1 - Random: chon deu trong cac cot hop le. Moc doi chung."""

from __future__ import annotations

import random

from connect_four.agents.base import Agent
from connect_four.game.base import ConnectFourGame


class RandomAgent(Agent):
    """Baseline: chon ngau nhien mot cot con trong.

    Khong tra ve cot day; seed giup lap lai cung chuoi lua chon.
    """

    name = "random"
    level = 1

    def __init__(self, seed: int | None = None) -> None:
        super().__init__(seed=seed)
        self._rng = random.Random(seed)

    def choose(self, game: ConnectFourGame) -> int:
        legal = game.legal_actions()
        if not legal:
            raise ValueError("Khong con nuoc di hop le.")
        action = self._rng.choice(legal)
        self.last_stats.nodes = 0
        self.last_stats.simulations = 0
        self.last_stats.depth_reached = 0
        return action
