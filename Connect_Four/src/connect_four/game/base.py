"""Hop dong API cua engine Connect Four.

Moi engine (bitboard nhanh, hoac ban tham chieu cham) deu phai cai dat day du
cac phuong thuc duoi day. Agent, giai dau va giao dien chi lam viec qua hop
dong nay, KHONG duoc truy cap truc tiep vao cau truc ben trong.

Loi ich: co the viet mot ban cham de doi chieu (crosscheck) voi ban bitboard,
va test co the chay tren ca hai ma khong sua gi.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Sequence

import numpy as np


class ConnectFourGame(ABC):
    """Giao dien engine toi thieu."""

    # ------------------------------------------------------------------
    # Vong doi van choi
    # ------------------------------------------------------------------
    @abstractmethod
    def reset(self) -> None:
        """Dua ban co ve trang thai ban dau, nguoi choi 1 di truoc."""

    @abstractmethod
    def legal_actions(self) -> list[int]:
        """Danh sach cot con cho duoc (chua day), thuong theo thu tu 0..6."""

    @abstractmethod
    def is_legal(self, action: int) -> bool:
        """True neu `action` la cot hop le o trang thai hien tai."""

    @abstractmethod
    def step(self, action: int) -> None:
        """Tha quan vao cot `action`.

        Raises:
            ValueError: cot khong hop le hoac van da ket thuc.
        """

    @abstractmethod
    def undo(self) -> None:
        """Hoan tac nuoc di gan nhat. Dung cho MCTS/mo phong."""

    @abstractmethod
    def clone(self) -> "ConnectFourGame":
        """Ban sao doc lap (thay doi ban sao khong anh huong ban goc)."""

    # ------------------------------------------------------------------
    # Trang thai va ket qua
    # ------------------------------------------------------------------
    @property
    @abstractmethod
    def board(self) -> np.ndarray:
        """Luoi (ROWS, COLS) dtype int8, hang 0 la hang duoi cung."""

    @property
    @abstractmethod
    def current_player(self) -> int:
        """Nguoi dang den luot: PLAYER_1 hoac PLAYER_2."""

    @abstractmethod
    def is_terminal(self) -> bool:
        """True khi co nguoi thang hoac ban co day."""

    @abstractmethod
    def winner(self) -> int | None:
        """PLAYER_1 / PLAYER_2 neu da co nguoi thang, nguoc lai None."""

    @abstractmethod
    def result(self, player: int) -> float:
        """Ket qua theo goc nhin `player`: thang +1.0, hoa 0.0, thua -1.0.

        Raises:
            ValueError: neu van chua ket thuc.
        """

    @abstractmethod
    def winning_moves(self, player: int) -> list[int]:
        """Cac cot giup `player` thang ngay o nuoc tiep theo (dung cho Heuristic)."""

    @abstractmethod
    def clone_after(self, action: int) -> "ConnectFourGame":
        """Tra ve ban sao da di `action` (tien loi cho tim kiem)."""

    # ------------------------------------------------------------------
    # Bieu dien
    # ------------------------------------------------------------------
    @abstractmethod
    def key(self) -> int:
        """Khoa hash cua trang thai (dung cho transposition table)."""

    @abstractmethod
    def to_array(self) -> np.ndarray:
        """Vector dac trung cho mang NN, gom ca thong tin luot di.

        Quy uoc: shape (2, ROWS, COLS), dtype float32, gom
        [quan cua nguoi dang di, quan cua doi thu].
        """

    @abstractmethod
    def render(self) -> str:
        """Chuoi ASCII de in ra terminal."""

    # ------------------------------------------------------------------
    @abstractmethod
    def moves_played(self) -> Sequence[int]:
        """Chuoi nuoc di tu dau van (de luu log va tai hien van dau)."""
