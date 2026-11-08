"""Engine nhanh bang bitboard 49-bit.

Cach bieu dien (ky thuat bitboard cua Pascal Pons):

    Moi cot chiem 7 bit: 6 o that (hang 0 = duoi cung ... hang 5) va 1 bit
    "dem" o tren cung luon bang 0. Bit cua o (hang r, cot c) nam o vi tri
    ``c * 7 + r`` trong mot so nguyen. Tong cong 7 cot x 7 bit = 49 bit.

         bit dem ->  6 13 20 27 34 41 48
         hang 5  ->  5 12 19 26 33 40 47
         ...
         hang 0  ->  0  7 14 21 28 35 42

    Moi nguoi choi co mot bitboard rieng (``_bb[0]`` cho PLAYER_1,
    ``_bb[1]`` cho PLAYER_2). ``_heights[c]`` la vi tri bit cua o trong tiep
    theo o cot c, nen tha quan = bat bit ``1 << _heights[c]``.

Kiem tra bon quan lien tiep bang dich bit: voi buoc dich ``s``, phep
``m = bb & (bb >> s)`` giu lai cac bit co hang xom cach ``s`` bit, roi
``m & (m >> 2s)`` giu lai cac bit dau cua mot day 4 quan. Bon buoc dich:

    s = 1  -> doc          s = 7  -> ngang
    s = 6  -> cheo xuong   s = 8  -> cheo len

Bit dem tren cung moi cot ngan khong cho day bit "cuon" tu cot nay sang cot
ke ben khi dich (vi vay moi cot can 7 bit chu khong phai 6).

Quy uoc khi van da ket thuc (giong ``ReferenceGame``): ``legal_actions()``
tra ve [], ``is_legal()`` tra ve False, ``step()`` nem ValueError.

Hop dong day du o ``connect_four.game.base.ConnectFourGame``.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np

from connect_four.game.base import ConnectFourGame
from connect_four.game.constants import COLS, PLAYER_1, PLAYER_2, PLAYERS, ROWS, other

_H = ROWS + 1  # 7 bit moi cot: 6 o + 1 bit dem
_SHIFTS = (1, _H, _H - 1, _H + 1)  # doc, ngang, cheo xuong, cheo len
_TOP_ROW_BIT = ROWS - 1  # bit cua hang tren cung trong moi cot (hang 5)
_COL_BASE = tuple(c * _H for c in range(COLS))  # bit dau cua tung cot


def _has_four(bb: int) -> bool:
    """True neu bitboard `bb` co 4 quan lien tiep theo mot trong 4 huong."""
    for s in _SHIFTS:
        m = bb & (bb >> s)
        if m & (m >> (2 * s)):
            return True
    return False


class ConnectFour(ConnectFourGame):
    """Engine bitboard - lop ma agent va giai dau su dung."""

    def __init__(self) -> None:
        self._bb: list[int] = [0, 0]  # bitboard cua PLAYER_1, PLAYER_2
        self._heights: list[int] = list(_COL_BASE)  # bit cua o trong tiep theo moi cot
        self._moves: list[int] = []
        self._winner: int | None = None

    # --- ham phu ----------------------------------------------------------
    @staticmethod
    def _is_valid_column(action: object) -> bool:
        if isinstance(action, bool) or not isinstance(action, (int, np.integer)):
            return False
        return 0 <= int(action) < COLS

    def _is_column_full(self, col: int) -> bool:
        return self._heights[col] == _COL_BASE[col] + ROWS

    def _player_index(self) -> int:
        """0 neu den luot PLAYER_1, 1 neu den luot PLAYER_2 (suy ra tu so nuoc da di)."""
        return len(self._moves) & 1

    # --- vong doi ---------------------------------------------------------
    def reset(self) -> None:
        self._bb = [0, 0]
        self._heights = list(_COL_BASE)
        self._moves = []
        self._winner = None

    def legal_actions(self) -> list[int]:
        if self.is_terminal():
            return []
        return [c for c in range(COLS) if not self._is_column_full(c)]

    def is_legal(self, action: int) -> bool:
        if not self._is_valid_column(action) or self.is_terminal():
            return False
        return not self._is_column_full(int(action))

    def step(self, action: int) -> None:
        if self.is_terminal():
            raise ValueError("Van da ket thuc, khong the di tiep")
        if not self._is_valid_column(action):
            raise ValueError(f"Cot khong hop le: {action!r} (can so nguyen 0..{COLS - 1})")
        col = int(action)
        if self._is_column_full(col):
            raise ValueError(f"Cot {col} da day")
        idx = self._player_index()
        self._bb[idx] |= 1 << self._heights[col]
        self._heights[col] += 1
        self._moves.append(col)
        if _has_four(self._bb[idx]):
            self._winner = PLAYERS[idx]

    def undo(self) -> None:
        if not self._moves:
            raise ValueError("Khong co nuoc di nao de hoan tac")
        col = self._moves.pop()
        self._heights[col] -= 1
        idx = self._player_index()  # sau khi pop: dung la nguoi vua di
        self._bb[idx] ^= 1 << self._heights[col]
        # Van chi dung lai khi co nguoi thang o nuoc cuoi; bo nuoc do thi het thang.
        self._winner = None

    def clone(self) -> "ConnectFourGame":
        new = ConnectFour.__new__(ConnectFour)
        new._bb = self._bb[:]
        new._heights = self._heights[:]
        new._moves = self._moves[:]
        new._winner = self._winner
        return new

    def clone_after(self, action: int) -> "ConnectFourGame":
        game = self.clone()
        game.step(action)
        return game

    # --- trang thai -------------------------------------------------------
    @property
    def board(self) -> np.ndarray:
        grid = np.zeros((ROWS, COLS), dtype=np.int8)
        for idx, player in enumerate(PLAYERS):
            bb = self._bb[idx]
            for c in range(COLS):
                for r in range(ROWS):
                    if (bb >> (_COL_BASE[c] + r)) & 1:
                        grid[r, c] = player
        return grid

    @property
    def current_player(self) -> int:
        return PLAYERS[self._player_index()]

    def is_terminal(self) -> bool:
        return self._winner is not None or len(self._moves) == ROWS * COLS

    def winner(self) -> int | None:
        return self._winner

    def result(self, player: int) -> float:
        if player not in PLAYERS:
            raise ValueError(f"Nguoi choi khong hop le: {player!r}")
        if not self.is_terminal():
            raise ValueError("Van chua ket thuc nen chua co ket qua")
        if self._winner is None:
            return 0.0
        return 1.0 if self._winner == player else -1.0

    def winning_moves(self, player: int) -> list[int]:
        if player not in PLAYERS:
            raise ValueError(f"Nguoi choi khong hop le: {player!r}")
        if self.is_terminal():
            return []
        bb = self._bb[PLAYERS.index(player)]
        return [
            c
            for c in range(COLS)
            if not self._is_column_full(c) and _has_four(bb | (1 << self._heights[c]))
        ]

    # --- bieu dien --------------------------------------------------------
    def key(self) -> int:
        """Khoa 49-bit: quan cua nguoi dang di + mat na tat ca quan.

        Voi hai so nay (va luot di suy ra tu so quan) suy ra duoc ban co,
        nen moi the co co dung mot khoa.
        """
        cur = self._bb[self._player_index()]
        return cur + (self._bb[0] | self._bb[1])

    def to_array(self) -> np.ndarray:
        grid = self.board
        me = self.current_player
        mine = (grid == me).astype(np.float32)
        theirs = (grid == other(me)).astype(np.float32)
        return np.stack([mine, theirs])

    def render(self) -> str:
        grid = self.board
        symbols = {0: ".", PLAYER_1: "X", PLAYER_2: "O"}
        lines = [
            " ".join(symbols[int(grid[r, c])] for c in range(COLS))
            for r in range(ROWS - 1, -1, -1)
        ]
        lines.append(" ".join(str(c) for c in range(COLS)))
        return "\n".join(lines)

    def moves_played(self) -> Sequence[int]:
        return tuple(self._moves)
