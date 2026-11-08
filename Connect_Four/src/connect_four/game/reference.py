"""Ban tham chieu cham, viet bang list thuong.

Muc dich KHONG phai de choi nhanh, ma de:
    - Lam "chuan dung" cho test crosscheck: cung mot chuoi nuoc di, engine
      bitboard va ban nay phai cho cung trang thai, cung nguoi thang.
    - De doc lai khi can hieu engine bitboard dang lam gi.

Cach lam (cu y don gian, uu tien ro rang):
    - `_grid[r][c]`: r = 0 la hang DUOI CUNG, gia tri EMPTY/PLAYER_1/PLAYER_2.
    - `_moves`: chuoi cot da di. Luot hien tai suy ra tu so nuoc da di.
    - Nguoi thang duoc tinh bang cach quet het 69 cua so 4 o
      (24 ngang + 21 doc + 12 cheo xuoi + 12 cheo nguoc), khong dung meo nao.

Quy uoc khi van da ket thuc: `legal_actions()` tra ve [] va `step()` nem
ValueError. Engine bitboard phai theo dung quy uoc nay.

Hop dong day du o `connect_four.game.base.ConnectFourGame`.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np

from connect_four.game.base import ConnectFourGame
from connect_four.game.constants import (
    COLS,
    EMPTY,
    PLAYER_1,
    PLAYER_2,
    PLAYERS,
    ROWS,
    WIN_LENGTH,
    other,
)


def _build_windows() -> list[tuple[tuple[int, int], ...]]:
    """Liet ke 69 cua so 4 o lien tiep (hang, cot) theo 4 huong."""
    windows: list[tuple[tuple[int, int], ...]] = []
    # (dr, dc): ngang, doc, cheo len-phai, cheo xuong-phai
    for dr, dc in ((0, 1), (1, 0), (1, 1), (-1, 1)):
        for r in range(ROWS):
            for c in range(COLS):
                end_r = r + dr * (WIN_LENGTH - 1)
                end_c = c + dc * (WIN_LENGTH - 1)
                if 0 <= end_r < ROWS and 0 <= end_c < COLS:
                    windows.append(
                        tuple((r + dr * k, c + dc * k) for k in range(WIN_LENGTH))
                    )
    return windows


_WINDOWS = _build_windows()
assert len(_WINDOWS) == 69, "Connect Four 7x6 phai co dung 69 cua so thang"


class ReferenceGame(ConnectFourGame):
    """Ban cham, de doi chieu. Uu tien ro rang hon toc do."""

    def __init__(self) -> None:
        self._grid: list[list[int]] = [[EMPTY] * COLS for _ in range(ROWS)]
        self._current = PLAYER_1
        self._moves: list[int] = []

    # ------------------------------------------------------------------
    # Ham phu (noi bo)
    # ------------------------------------------------------------------
    @staticmethod
    def _is_valid_column(action: object) -> bool:
        """True neu `action` la so nguyen (int hoac numpy int) trong 0..COLS-1."""
        if isinstance(action, bool) or not isinstance(action, (int, np.integer)):
            return False
        return 0 <= int(action) < COLS

    def _column_height(self, col: int) -> int:
        """So quan dang nam trong cot `col`."""
        return sum(1 for r in range(ROWS) if self._grid[r][col] != EMPTY)

    def _has_won(self, player: int) -> bool:
        """True neu `player` co it nhat mot cua so 4 quan cua minh."""
        return any(
            all(self._grid[r][c] == player for r, c in window) for window in _WINDOWS
        )

    def _is_full(self) -> bool:
        """Ban co day khi hang tren cung khong con o trong."""
        return all(self._grid[ROWS - 1][c] != EMPTY for c in range(COLS))

    # ------------------------------------------------------------------
    # Vong doi van choi
    # ------------------------------------------------------------------
    def reset(self) -> None:
        self._grid = [[EMPTY] * COLS for _ in range(ROWS)]
        self._current = PLAYER_1
        self._moves = []

    def legal_actions(self) -> list[int]:
        if self.is_terminal():
            return []
        return [c for c in range(COLS) if self._grid[ROWS - 1][c] == EMPTY]

    def is_legal(self, action: int) -> bool:
        if not self._is_valid_column(action):
            return False
        return int(action) in self.legal_actions()

    def step(self, action: int) -> None:
        if self.is_terminal():
            raise ValueError("Van da ket thuc, khong the di tiep")
        if not self._is_valid_column(action):
            raise ValueError(f"Cot khong hop le: {action!r} (can so nguyen 0..{COLS - 1})")
        col = int(action)
        row = self._column_height(col)
        if row >= ROWS:
            raise ValueError(f"Cot {col} da day")
        self._grid[row][col] = self._current
        self._moves.append(col)
        self._current = other(self._current)

    def undo(self) -> None:
        if not self._moves:
            raise ValueError("Khong co nuoc di nao de hoan tac")
        col = self._moves.pop()
        row = self._column_height(col) - 1  # quan tren cung cua cot
        self._grid[row][col] = EMPTY
        self._current = other(self._current)

    def clone(self) -> "ConnectFourGame":
        other_game = ReferenceGame()
        other_game._grid = [row[:] for row in self._grid]  # sao chep sau
        other_game._current = self._current
        other_game._moves = self._moves[:]
        return other_game

    def clone_after(self, action: int) -> "ConnectFourGame":
        game = self.clone()
        game.step(action)
        return game

    # ------------------------------------------------------------------
    # Trang thai va ket qua
    # ------------------------------------------------------------------
    @property
    def board(self) -> np.ndarray:
        # np.array(...) tao ban sao, sua ket qua khong anh huong ban co.
        return np.array(self._grid, dtype=np.int8)

    @property
    def current_player(self) -> int:
        return self._current

    def is_terminal(self) -> bool:
        return self.winner() is not None or self._is_full()

    def winner(self) -> int | None:
        for player in PLAYERS:
            if self._has_won(player):
                return player
        return None

    def result(self, player: int) -> float:
        if player not in PLAYERS:
            raise ValueError(f"Nguoi choi khong hop le: {player!r}")
        if not self.is_terminal():
            raise ValueError("Van chua ket thuc nen chua co ket qua")
        win = self.winner()
        if win is None:
            return 0.0
        return 1.0 if win == player else -1.0

    def winning_moves(self, player: int) -> list[int]:
        if player not in PLAYERS:
            raise ValueError(f"Nguoi choi khong hop le: {player!r}")
        if self.is_terminal():
            return []
        moves: list[int] = []
        for col in range(COLS):
            row = self._column_height(col)
            if row >= ROWS:
                continue
            self._grid[row][col] = player  # tha thu
            if self._has_won(player):
                moves.append(col)
            self._grid[row][col] = EMPTY  # tra lai nhu cu
        return moves

    # ------------------------------------------------------------------
    # Bieu dien
    # ------------------------------------------------------------------
    def key(self) -> int:
        """Ma hoa luoi theo he co so 3. Luot di suy ra duoc tu luoi nen khong can them."""
        value = 0
        for r in range(ROWS):
            for c in range(COLS):
                value = value * 3 + self._grid[r][c]
        return value

    def to_array(self) -> np.ndarray:
        grid = self.board
        mine = (grid == self._current).astype(np.float32)
        theirs = (grid == other(self._current)).astype(np.float32)
        return np.stack([mine, theirs])  # shape (2, ROWS, COLS)

    def render(self) -> str:
        symbols = {EMPTY: ".", PLAYER_1: "X", PLAYER_2: "O"}
        lines = [
            " ".join(symbols[self._grid[r][c]] for c in range(COLS))
            for r in range(ROWS - 1, -1, -1)  # in hang tren cung truoc
        ]
        lines.append(" ".join(str(c) for c in range(COLS)))
        return "\n".join(lines)

    # ------------------------------------------------------------------
    def moves_played(self) -> Sequence[int]:
        return tuple(self._moves)
