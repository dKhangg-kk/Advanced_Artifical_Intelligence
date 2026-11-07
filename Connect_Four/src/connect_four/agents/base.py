"""Giao dien chung cho ca sau tac tu.

Moi tac tu chi can cai dat `choose(game) -> cot`. Viec con lai (chon nuoc,
do thoi gian, ghi log) do giai dau dam nhan.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from connect_four.game.base import ConnectFourGame


@dataclass(frozen=True)
class Budget:
    """Ngan sach tinh toan cho mot nuoc di.

    Chi dung mot trong ba kieu:
        Budget(depth=5)              # gioi han do sau (Alpha-Beta)
        Budget(simulations=1000)     # gioi han so mo phong (MCTS)
        Budget(time_s=1.0)           # gioi han thoi gian (che do so sanh cong bang)
    """

    depth: int | None = None
    simulations: int | None = None
    time_s: float | None = None

    def __post_init__(self) -> None:
        given = [v for v in (self.depth, self.simulations, self.time_s) if v is not None]
        if len(given) > 1:
            raise ValueError("Chi duoc dat mot trong depth / simulations / time_s")


@dataclass
class SearchStats:
    """Thong ke cua mot nuoc di, ghi vao log de phan tich."""

    nodes: int = 0
    simulations: int = 0
    depth_reached: int = 0
    time_ms: float = 0.0
    extra: dict[str, float] = field(default_factory=dict)


class Agent(ABC):
    """Tac tu chon nuoc.

    Quy uoc:
        - `choose()` KHONG duoc sua trang thai `game` (dung clone/undo neu can).
        - Chi duoc tra ve cot nam trong `game.legal_actions()`.
        - Sau moi lan goi, `last_stats` phai duoc cap nhat.
    """

    name: str = "base"
    level: int = 0

    def __init__(self, budget: Budget | None = None, seed: int | None = None) -> None:
        self.budget = budget or Budget()
        self.seed = seed
        self.last_stats = SearchStats()

    @abstractmethod
    def choose(self, game: ConnectFourGame) -> int:
        """Tra ve chi so cot se tha quan."""

    def reset(self) -> None:
        """Xoa trang thai hoc/tich luy giua cac van (neu co)."""
        self.last_stats = SearchStats()

    def __repr__(self) -> str:
        return f"{type(self).__name__}(budget={self.budget!r})"
