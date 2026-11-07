"""Cac do luong thong ke dung trong giai dau va bao cao.

Tat ca ham o day la ham thuan (khong phu thuoc numpy/engine) de test de dang.
"""

from __future__ import annotations

import math
from collections.abc import Sequence


def score(wins: int, draws: int, total: int) -> float:
    """Diem doi khang: (thang + 0.5 * hoa) / tong so van."""
    if total <= 0:
        raise ValueError("total phai > 0")
    return (wins + 0.5 * draws) / total


def win_rate(wins: int, total: int) -> float:
    """Ty le thang thuan (khong tinh hoa)."""
    if total <= 0:
        raise ValueError("total phai > 0")
    return wins / total


def wilson_interval(wins: float, total: int, z: float = 1.96) -> tuple[float, float]:
    """Khoang tin cay Wilson cho mot ty le.

    Dung Wilson thay vi xap xi chuan vi no dung duoc khi ty le gan 0 hoac 1
    (truong hop pho bien: mot tac tu thang 200/200 van).
    """
    raise NotImplementedError("TODO: cai dat cong thuc Wilson")


def bootstrap_ci(samples: Sequence[float], n_resamples: int = 10_000, alpha: float = 0.05,
                 seed: int | None = None) -> tuple[float, float]:
    """Khoang tin cay bootstrap percentile cho trung binh."""
    raise NotImplementedError("TODO: cai dat bootstrap")


def percentile(values: Sequence[float], q: float) -> float:
    """Phan vi `q` (0..100), dung phuong phap nearest-rank (khong noi suy)."""
    if not values:
        raise ValueError("values rong")
    if not 0 <= q <= 100:
        raise ValueError("q phai trong [0, 100]")
    ordered = sorted(float(value) for value in values)
    rank = math.ceil(q / 100.0 * len(ordered)) - 1
    return ordered[min(max(rank, 0), len(ordered) - 1)]


def p95(values: Sequence[float]) -> float:
    """Do tre phan vi 95 - chi so bat buoc trong bao cao."""
    return percentile(values, 95.0)


def mean(values: Sequence[float]) -> float:
    """Trung binh, tra 0.0 khi rong."""
    if not values:
        return 0.0
    return math.fsum(values) / len(values)
