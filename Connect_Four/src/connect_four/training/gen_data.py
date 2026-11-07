"""Sinh nhan (label) nuoc di bang Alpha-Beta de huan luyen cap 5.

Nguyen tac da chot trong README:
    - Alpha-Beta tu choi (self-play) hoac theo khai cuoc ngau nhien.
    - Chia train/val/test THEO VAN (khong tron trang thai giua cac tap).
    - Kiem soat trang thai trung giua cac tap, ghi lai ty le thuc te sau loc.
    - Chi tang cuong doi xung (lat guong) trong tap train, va phai doi nhan cot.
    - Nhan phan anh tac tu Alpha-Beta o do sau co dinh, KHONG phai nuoc toi uu
      toan hoc - phai ghi ro dieu nay trong bao cao.
"""

from __future__ import annotations

from pathlib import Path


def generate_dataset(
    n_games: int,
    depth: int = 4,
    max_plies_random: int = 4,
    out_dir: str | Path = "data/generated",
    seed: int = 0,
) -> Path:
    """Sinh `n_games` van, luu moi van mot file (hoac mot parquet theo van).

    Returns:
        Thu muc (hoac file) da ghi.
    """
    raise NotImplementedError("TODO: self-play voi Alpha-Beta va luu nhan theo van")


def split_by_game(
    dataset_dir: str | Path,
    ratios: tuple[float, float, float] = (0.70, 0.15, 0.15),
    seed: int = 0,
) -> tuple[list[int], list[int], list[int]]:
    """Chia tap theo VAN, kiem tra trung trang thai, tra ve 3 danh sach game_id."""
    raise NotImplementedError("TODO: chia theo van + bao cao trang thai trung")
