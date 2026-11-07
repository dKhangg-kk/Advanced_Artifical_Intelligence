"""Cap 5 - Neural Network: hoc co giam sat de du doan nuoc di.

Nhan (label) sinh tu Alpha-Beta o do sau co dinh, luu theo VAN (khong tron
trang thai giua train/val/test).

LUU Y: torch chi duoc import BEN TRONG __init__ / choose, de `import connect_four`
va `pytest` van chay duoc khi may chua cai torch (vi du tren CI).
"""

from __future__ import annotations

from pathlib import Path

from connect_four.agents.base import Agent
from connect_four.game.base import ConnectFourGame


class PolicyNet:
    """Mang policy: input (2, 6, 7) -> logits 7 cot.

    Goi y kien truc: conv 3x3 (32 -> 64 kenh) + BatchNorm + ReLU,
    flatten + linear -> 7 logits.
    """

    def __init__(self) -> None:
        raise NotImplementedError("TODO: dinh nghia mang bang torch.nn (import ben trong)")


class NNAgent(Agent):
    """Tac tu dung mang policy da huan luyen (cap 5)."""

    name = "nn"
    level = 5

    def __init__(self, checkpoint: str | Path | None = None, seed: int | None = None) -> None:
        super().__init__(seed=seed)
        self.checkpoint = Path(checkpoint) if checkpoint else None
        self._model = None

    def choose(self, game: ConnectFourGame) -> int:
        raise NotImplementedError("TODO: nap checkpoint, argmax tren cot hop le")
