"""Thanh phan co ban cho huan luyen Deep Q-Network (DQN), cap 6.

Y1 cung cap ReplayBuffer va EpsilonSchedule khong phu thuoc PyTorch. Vong lap
huan luyen day du (tuong tac game, Bellman update, Target Network, checkpoint)
se duoc trien khai o buoc Y3.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import math
from pathlib import Path
import random
from typing import Deque

import numpy as np

from connect_four.game.constants import COLS, ROWS


@dataclass(frozen=True)
class DQNTransition:
    """Mot mau trai nghiem va mat na hanh dong hop le cua trang thai ke tiep."""

    state: np.ndarray
    action: int
    reward: float
    next_state: np.ndarray
    done: bool
    next_legal_mask: np.ndarray


def _copy_state(value: np.ndarray, field_name: str) -> np.ndarray:
    """Kiem tra va sao chep state theo quy uoc (2, 6, 7)."""
    state = np.asarray(value, dtype=np.float32)
    expected_shape = (2, ROWS, COLS)
    if state.shape != expected_shape:
        raise ValueError(f"{field_name} phai co shape {expected_shape}, nhan duoc {state.shape}.")
    if not np.isfinite(state).all():
        raise ValueError(f"{field_name} chi duoc chua gia tri huu han.")
    return state.copy()


def _copy_legal_mask(value: np.ndarray, done: bool) -> np.ndarray:
    """Kiem tra mask 7 cot; trang thai terminal co the khong con cot hop le."""
    mask = np.asarray(value, dtype=np.bool_)
    if mask.shape != (COLS,):
        raise ValueError(f"next_legal_mask phai co shape ({COLS},), nhan duoc {mask.shape}.")
    if not done and not bool(mask.any()):
        raise ValueError("Transition chua ket thuc phai co it nhat mot cot hop le o next_state.")
    return mask.copy()


class ReplayBuffer:
    """Bo nho kinh nghiem DQN theo FIFO, mac dinh toi da 100.000 transition.

    Khi day, transition moi se ghi de phan tu cu nhat. ``sample(batch_size)``
    lay ngau nhien khong hoan lai va tra ve dung so mau duoc yeu cau.
    """

    def __init__(self, capacity: int = 100_000, seed: int | None = None) -> None:
        if isinstance(capacity, bool) or not isinstance(capacity, int) or capacity <= 0:
            raise ValueError("capacity phai la so nguyen duong.")
        self.capacity = capacity
        self._memory: Deque[DQNTransition] = deque(maxlen=capacity)
        self._rng = random.Random(seed)

    def __len__(self) -> int:
        return len(self._memory)

    def add(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool,
        next_legal_mask: np.ndarray,
    ) -> None:
        """Them mot transition; tu dong sao chep cac mang dau vao.

        ``next_legal_mask`` la bool mask cua BAN KE TIEP, khong phai ban hien tai.
        O trang thai ket thuc, mask co the gom toan False.
        """
        if isinstance(action, bool) or not isinstance(action, (int, np.integer)):
            raise ValueError("action phai la so nguyen trong khoang 0..6.")
        action = int(action)
        if not 0 <= action < COLS:
            raise ValueError("action phai nam trong khoang 0..6.")
        if not isinstance(done, (bool, np.bool_)):
            raise ValueError("done phai la gia tri bool.")
        reward = float(reward)
        if not math.isfinite(reward):
            raise ValueError("reward phai la so huu han.")

        transition = DQNTransition(
            state=_copy_state(state, "state"),
            action=action,
            reward=reward,
            next_state=_copy_state(next_state, "next_state"),
            done=bool(done),
            next_legal_mask=_copy_legal_mask(next_legal_mask, bool(done)),
        )
        self._memory.append(transition)

    def push(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool,
        next_legal_mask: np.ndarray,
    ) -> None:
        """Alias thong dung cua ``add()``."""
        self.add(state, action, reward, next_state, done, next_legal_mask)

    def sample(self, batch_size: int) -> list[DQNTransition]:
        """Lay ngau nhien batch khong lap; loi neu buffer chua du mau."""
        if isinstance(batch_size, bool) or not isinstance(batch_size, int) or batch_size <= 0:
            raise ValueError("batch_size phai la so nguyen duong.")
        if batch_size > len(self._memory):
            raise ValueError(
                f"Khong du transition de lay batch: can {batch_size}, hien co {len(self._memory)}."
            )
        return self._rng.sample(list(self._memory), batch_size)

    def clear(self) -> None:
        """Xoa toan bo transition dang luu."""
        self._memory.clear()


@dataclass
class EpsilonSchedule:
    """Lich epsilon giam theo episode, co san toi thieu 0.05.

    ``value`` ban dau bang ``start``; moi lan goi ``step()`` tuong ung ket thuc
    mot episode va nhan epsilon voi ``decay`` truoc khi ap san ``minimum``.
    """

    start: float = 1.0
    minimum: float = 0.05
    decay: float = 0.9995
    episode: int = 0

    def __post_init__(self) -> None:
        self.start = float(self.start)
        self.minimum = float(self.minimum)
        self.decay = float(self.decay)
        if not (0.0 <= self.minimum <= self.start <= 1.0):
            raise ValueError("Can thoa 0 <= minimum <= start <= 1.")
        if not (0.0 < self.decay <= 1.0):
            raise ValueError("decay phai nam trong khoang (0, 1].")
        if isinstance(self.episode, bool) or not isinstance(self.episode, int) or self.episode < 0:
            raise ValueError("episode phai la so nguyen khong am.")

    @property
    def value(self) -> float:
        """Epsilon hien tai sau ``episode`` lan cap nhat."""
        return max(self.minimum, self.start * (self.decay ** self.episode))

    def step(self) -> float:
        """Tien them mot episode va tra ve epsilon moi."""
        self.episode += 1
        return self.value

    def reset(self) -> None:
        """Dat lich ve episode 0 va epsilon ban dau."""
        self.episode = 0


def epsilon_for_episode(
    episode: int,
    start: float = 1.0,
    minimum: float = 0.05,
    decay: float = 0.9995,
) -> float:
    """Tinh epsilon truc tiep tai episode (episode 0 la gia tri start)."""
    schedule = EpsilonSchedule(start=start, minimum=minimum, decay=decay)
    if isinstance(episode, bool) or not isinstance(episode, int) or episode < 0:
        raise ValueError("episode phai la so nguyen khong am.")
    return max(schedule.minimum, schedule.start * (schedule.decay ** episode))


def train_dqn(
    episodes: int = 10_000,
    opponent: str = "heuristic",
    lr: float = 1e-4,
    gamma: float = 0.99,
    epsilon_start: float = 1.0,
    epsilon_min: float = 0.05,
    epsilon_decay: float = 0.9995,
    buffer_size: int = 100_000,
    batch_size: int = 64,
    target_update_freq: int = 500,
    checkpoint_milestones: tuple[int, ...] = (1_000, 2_500, 5_000, 10_000),
    out_dir: str | Path = "checkpoints/level6_dqn",
    seed: int = 0,
) -> Path:
    """Vong lap huan luyen day du se duoc bo sung o nhiem vu Y3."""
    raise NotImplementedError(
        "Y3: can cai dat vong tuong tac game, Bellman update, Target Network va checkpoint."
    )
