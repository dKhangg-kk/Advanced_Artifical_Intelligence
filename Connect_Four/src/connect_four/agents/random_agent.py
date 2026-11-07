"""Cap 1 - Random: chon deu trong cac cot hop le. Moc doi chung."""

from __future__ import annotations

import random

from connect_four.agents.base import Agent
from connect_four.game.base import ConnectFourGame


class RandomAgent(Agent):
    """Baseline: chon ngau nhien mot cot con trong.

    Xong khi: khong bao gio tra ve cot day; thang duoc 0% truoc Heuristic
    o 200 van (chi de xac nhan moi thu noi dung).
    """

    name = "random"
    level = 1

    def __init__(self, seed: int | None = None) -> None:
        super().__init__(seed=seed)
        self._rng = random.Random(seed)

    def choose(self, game: ConnectFourGame) -> int:
        raise NotImplementedError("TODO: chon ngau nhien trong game.legal_actions()")
