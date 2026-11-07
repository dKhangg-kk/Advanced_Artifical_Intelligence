"""Cai dat engine nhanh bang bitboard 49-bit.

KHUNG - chua co thuat toan. Moi phuong thuc dang `raise NotImplementedError`.
Xem hop dong day du o `connect_four.game.base.ConnectFourGame`.

Goi y cai dat:
    - Moi cot chiem 7 bit (6 o + 1 bit "full" o tren cung) trong mot so uint64.
    - Kiem tra 4 quan bang dich bit (ky thuat bitboard cua Pascal Pons).
    - `key()` = ghep 2 so bitboard cua 2 nguoi choi.
    - Giu them `_moves` list de `undo()` va `moves_played()`.

Thu tu lam de:
    1. reset/board/current_player
    2. legal_actions/is_legal/step/undo/moves_played
    3. is_terminal/winner/result
    4. winning_moves
    5. key/to_array/render/clone
    6. Doi chieu voi `ReferenceGame` bang test crosscheck.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np

from connect_four.game.base import ConnectFourGame
from connect_four.game.constants import PLAYER_1

_TODO = "TODO: cai dat engine bitboard (xem docstring dau file)"


class ConnectFour(ConnectFourGame):
    """Engine bitboard - lop ma agent va giai dau su dung."""

    def __init__(self) -> None:
        self._board = np.zeros((6, 7), dtype=np.int8)
        self._current = PLAYER_1
        self._moves: list[int] = []

    # --- vong doi ---------------------------------------------------------
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

    # --- trang thai -------------------------------------------------------
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

    # --- bieu dien --------------------------------------------------------
    def key(self) -> int:
        raise NotImplementedError(_TODO)

    def to_array(self) -> np.ndarray:
        raise NotImplementedError(_TODO)

    def render(self) -> str:
        raise NotImplementedError(_TODO)

    def moves_played(self) -> Sequence[int]:
        raise NotImplementedError(_TODO)
