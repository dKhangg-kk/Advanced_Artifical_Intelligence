"""Ban tham chieu cham, viet bang list thuong.

Muc dich KHONG phai de choi nhanh, ma de:
    - Lam "chuan dung" cho test crosscheck: cung mot chuoi nuoc di, engine
      bitboard va ban nay phai cho cung trang thai, cung nguoi thang.
    - De doc lai khi can hieu engine bitboard dang lam gi.

KHUNG - chua cai dat. Xem hop dong o `connect_four.game.base.ConnectFourGame`.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np

from connect_four.game.base import ConnectFourGame
from connect_four.game.constants import COLS, PLAYER_1, ROWS

_TODO = "TODO: cai dat ban tham chieu bang list 2 chieu"


class ReferenceGame(ConnectFourGame):
    """Ban cham, de doi chieu. Uu tien ro rang hon toc do."""

    def __init__(self) -> None:
        self._grid: list[list[int]] = [[0] * COLS for _ in range(ROWS)]
        self._current = PLAYER_1
        self._moves: list[int] = []

    def reset(self) -> None:
        raise NotImplementedError(_TODO)

    def legal_actions(self) -> list[int]:
        raise NotImplementedError(_TODO)

    def is_legal(self, action: int) -> bool:
        raise NotImplementedError(_TODO)

    def step(self, action: int) -> None:
        raise NotImplementedError(_TODO)

    def undo(self) -> None:
        raise NotImplementedError(_TODO)

    def clone(self) -> "ConnectFourGame":
        raise NotImplementedError(_TODO)

    def clone_after(self, action: int) -> "ConnectFourGame":
        raise NotImplementedError(_TODO)

    @property
    def board(self) -> np.ndarray:
        raise NotImplementedError(_TODO)

    @property
    def current_player(self) -> int:
        raise NotImplementedError(_TODO)

    def is_terminal(self) -> bool:
        raise NotImplementedError(_TODO)

    def winner(self) -> int | None:
        raise NotImplementedError(_TODO)

    def result(self, player: int) -> float:
        raise NotImplementedError(_TODO)

    def winning_moves(self, player: int) -> list[int]:
        raise NotImplementedError(_TODO)

    def key(self) -> int:
        raise NotImplementedError(_TODO)

    def to_array(self) -> np.ndarray:
        raise NotImplementedError(_TODO)

    def render(self) -> str:
        raise NotImplementedError(_TODO)

    def moves_played(self) -> Sequence[int]:
        raise NotImplementedError(_TODO)
