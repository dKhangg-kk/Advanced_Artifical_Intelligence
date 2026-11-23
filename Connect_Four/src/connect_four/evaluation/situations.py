"""Phan loai the co policy theo tinh huong chien thuat (RQ2).

Module chi dung NumPy va khong phu thuoc PyTorch de CI nhe van kiem thu duoc.
Moi the co duoc bieu dien bang mang ``(2, ROWS, COLS)`` giong ``to_array()``:
kenh 0 la quan cua nguoi dang di, kenh 1 la quan doi thu.

Bon nhom tinh huong duoc dung trong ablation A3:

``win_now``
    Nguoi dang di co it nhat mot cot thang ngay.
``block``
    Nguoi dang di khong thang ngay, nhung doi thu co it nhat mot cot thang
    ngay nen phai chan.
``center_control``
    Khong co nuoc thang/chan ngay, cot giua (3) con trong.
``other``
    Cac the co con lai.

Voi ``win_now`` va ``block``, du doan duoc coi la dung neu no nam trong tap
nuoc thang/chan tuong ung (khong bat buoc trung nhan Alpha-Beta neu co nhieu
nuoc cung thoa). Voi ``center_control``, du doan dung la cot giua; day la
dai dien cho ky nang kiem soat trung tam. Voi ``other``, dung khi trung nhan.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

from connect_four.game.constants import COLS, ROWS, WIN_LENGTH

SITUATION_NAMES: tuple[str, ...] = ("win_now", "block", "center_control", "other")
CENTER_COLUMN = COLS // 2
_DIRECTIONS = ((0, 1), (1, 0), (1, 1), (1, -1))


@dataclass(frozen=True)
class Situation:
    """Thong tin tinh huong cua mot the co."""

    name: str
    legal_actions: tuple[int, ...]
    winning_moves: tuple[int, ...]
    blocking_moves: tuple[int, ...]
    center_available: bool


def _as_state(state: object) -> np.ndarray:
    array = np.asarray(state)
    if array.shape != (2, ROWS, COLS):
        raise ValueError(
            f"state phai co shape (2, {ROWS}, {COLS}), nhan duoc {array.shape}."
        )
    if not np.isin(array, (0, 1)).all():
        raise ValueError("state chi duoc chua gia tri 0/1.")
    if np.any(array[0].astype(bool) & array[1].astype(bool)):
        raise ValueError("hai kenh state khong duoc chong quan len nhau.")
    return array.astype(np.int8, copy=False)


def _column_height(state: np.ndarray, column: int) -> int:
    return int(state[0, :, column].sum() + state[1, :, column].sum())


def _would_win(channel: np.ndarray, row: int, column: int) -> bool:
    """True neu dat quan tai (row, column) tao duoc 4 quan lien tiep."""
    for row_step, column_step in _DIRECTIONS:
        count = 1
        for sign in (1, -1):
            current_row = row + sign * row_step
            current_column = column + sign * column_step
            while (
                0 <= current_row < ROWS
                and 0 <= current_column < COLS
                and channel[current_row, current_column]
            ):
                count += 1
                current_row += sign * row_step
                current_column += sign * column_step
        if count >= WIN_LENGTH:
            return True
    return False


def _winning_columns(
    state: np.ndarray,
    channel_index: int,
    legal_actions: Iterable[int],
) -> tuple[int, ...]:
    channel = state[channel_index]
    winning: list[int] = []
    for column in legal_actions:
        row = _column_height(state, column)
        if row < ROWS and _would_win(channel, row, column):
            winning.append(column)
    return tuple(winning)


def classify_position(state: object) -> Situation:
    """Phan loai mot the co theo thu tu uu tien win > block > center > other."""
    array = _as_state(state)
    legal_actions = tuple(
        column for column in range(COLS) if _column_height(array, column) < ROWS
    )
    winning_moves = _winning_columns(array, 0, legal_actions)
    if winning_moves:
        return Situation(
            name="win_now",
            legal_actions=legal_actions,
            winning_moves=winning_moves,
            blocking_moves=(),
            center_available=CENTER_COLUMN in legal_actions,
        )

    blocking_moves = _winning_columns(array, 1, legal_actions)
    if blocking_moves:
        return Situation(
            name="block",
            legal_actions=legal_actions,
            winning_moves=(),
            blocking_moves=blocking_moves,
            center_available=CENTER_COLUMN in legal_actions,
        )

    center_available = CENTER_COLUMN in legal_actions
    return Situation(
        name="center_control" if center_available else "other",
        legal_actions=legal_actions,
        winning_moves=(),
        blocking_moves=(),
        center_available=center_available,
    )


def situation_hit(situation: Situation, action: int, label: int) -> bool:
    """Danh gia mot nuoc du doan co dat yeu cau cua tinh huong hay khong."""
    if action not in situation.legal_actions:
        return False
    if situation.name == "win_now":
        return action in situation.winning_moves
    if situation.name == "block":
        return action in situation.blocking_moves
    if situation.name == "center_control":
        return action == CENTER_COLUMN
    return action == label


def situation_metrics(
    states: np.ndarray,
    labels: np.ndarray,
    predictions: np.ndarray,
) -> dict[str, float]:
    """Tinh so mau va do chinh xac tung tinh huong.

    Tra ve 12 chi so dang ``<situation>_n``, ``<situation>_top1_accuracy`` va
    ``<situation>_situation_accuracy``. ``top1_accuracy`` so khop nhan
    Alpha-Beta; ``situation_accuracy`` danh gia dung yeu cau chien thuat nhu mo
    ta o dau module. Tinh huong khong xuat hien co ``n=0`` va accuracy ``0.0``
    de JSON/CSV luon huu han.
    """
    state_array = np.asarray(states)
    label_array = np.asarray(labels)
    prediction_array = np.asarray(predictions)
    if state_array.ndim != 4 or state_array.shape[1:] != (2, ROWS, COLS):
        raise ValueError(
            f"states phai co shape (N, 2, {ROWS}, {COLS}), nhan duoc {state_array.shape}."
        )
    if label_array.shape != (state_array.shape[0],):
        raise ValueError("labels phai co shape (N,).")
    if prediction_array.shape != label_array.shape:
        raise ValueError("predictions phai co shape (N,).")

    counts = {name: 0 for name in SITUATION_NAMES}
    top1_correct = {name: 0 for name in SITUATION_NAMES}
    situation_correct = {name: 0 for name in SITUATION_NAMES}

    for state, label, prediction in zip(
        state_array, label_array, prediction_array, strict=True
    ):
        situation = classify_position(state)
        action = int(prediction)
        target = int(label)
        counts[situation.name] += 1
        top1_correct[situation.name] += int(action == target)
        situation_correct[situation.name] += int(
            situation_hit(situation, action, target)
        )

    metrics: dict[str, float] = {}
    for name in SITUATION_NAMES:
        count = counts[name]
        metrics[f"{name}_n"] = float(count)
        metrics[f"{name}_top1_accuracy"] = (
            top1_correct[name] / count if count else 0.0
        )
        metrics[f"{name}_situation_accuracy"] = (
            situation_correct[name] / count if count else 0.0
        )
    return metrics


__all__ = [
    "CENTER_COLUMN",
    "SITUATION_NAMES",
    "Situation",
    "classify_position",
    "situation_hit",
    "situation_metrics",
]
