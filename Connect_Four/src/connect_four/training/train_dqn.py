"""Cap 6 - Huan luyen bang Deep Q-Network (DQN).

Thiet ke chi tiet theo Proposal:
    - Moi episode = mot van dau tuong tac giua DQN va doi thu (Self-play hoac
      doi thu Random, Heuristic, Alpha-Beta).
    - Phan thuong (Reward): xac dinh cuoi van theo goc nhin cua DQN:
      thang +1.0, hoa 0.0, thua -1.0 (co the dinh hinh phan thuong buoc di hop le nhe neu can).
    - Replay Buffer: luu tru transition (s, a, r, s', done), kich thuoc toi da 100.000.
    - Target Network: duoc dong bang va dong bo dinh ky voi Policy Network moi C buoc
      (vi du: moi 500 buoc hoac moi 50 episodes).
    - Kham pha: Epsilon-Greedy bat dau tu 1.0, giam dan theo he so decay ve 0.05.
    - Danh gia va luu checkpoint: tai cac moc dinh ky (1.000, 2.500, 5.000, 10.000 episodes)
      tren tap cac van dau doc lap voi seed co dinh.

Trang thai cai dat:
    - [Y1] ReplayBuffer va lich epsilon (`epsilon_at`, `episodes_to_floor`): DA XONG.
    - [Y3] Vong lap huan luyen `train_dqn`: CHUA LAM (con la khung).

LUU Y: file nay chi dung numpy o muc module; torch (neu can) phai import ben trong
ham de `import connect_four` va `pytest` van chay duoc khi may chua cai torch.
"""

from __future__ import annotations

import math
import operator
from pathlib import Path
from typing import NamedTuple

import numpy as np

from connect_four.game.constants import COLS, ROWS

# Gia tri mac dinh theo Proposal (train_dqn ben duoi dung cung cac so nay).
BUFFER_SIZE = 100_000   # suc chua toi da cua Replay Buffer
EPSILON_START = 1.0     # epsilon ban dau: kham pha hoan toan
EPSILON_MIN = 0.05      # san epsilon: luon giu lai 5% kham pha
EPSILON_DECAY = 0.9995  # he so nhan epsilon sau MOI EPISODE

STATE_SHAPE = (2, ROWS, COLS)  # (quan nguoi dang di, quan doi thu) x hang x cot


# ---------------------------------------------------------------------------
# Replay Buffer
# ---------------------------------------------------------------------------
class Batch(NamedTuple):
    """Mot lo transition lay mau tu buffer (B = batch_size).

    Cac mang deu la numpy, torch chi duoc dung sau khi train_dqn doi sang tensor.
    """

    states: np.ndarray       # (B, 2, 6, 7) float32 - trang thai s
    actions: np.ndarray      # (B,) int64 - cot da tha, 0..6
    rewards: np.ndarray      # (B,) float32 - phan thuong r
    next_states: np.ndarray  # (B, 2, 6, 7) float32 - trang thai s' (sau luot doi thu)
    dones: np.ndarray        # (B,) float32 - 1.0 neu van ket thuc, nguoc lai 0.0
    next_masks: np.ndarray   # (B, 7) bool - cot hop le cua ban co s' (True = duoc di)


class ReplayBuffer:
    """Bo nho trai nghiem dang vong (ring buffer) cho DQN.

    - Chua toi da `capacity` transition (mac dinh 100.000). Khi day, transition
      moi se GHI DE transition CU NHAT.
    - Moi transition luu them mat na cot hop le cua ban co ke tiep (`next_mask`)
      de tinh max_{a' hop le} Q_target(s', a') trong muc tieu Bellman ma khong
      phai dung lai engine luc huan luyen.
    - `sample(n)` tra ve DUNG n transition khac nhau, chon deu ngau nhien.

    Bo nho: moi transition khoang 700 byte -> 100.000 transition khoang 70 MB.
    """

    def __init__(self, capacity: int = BUFFER_SIZE, seed: int | None = None) -> None:
        capacity = operator.index(capacity)
        if capacity <= 0:
            raise ValueError(f"capacity phai > 0, nhan duoc {capacity}.")
        self.capacity = capacity
        self._rng = np.random.default_rng(seed)

        self._states = np.zeros((capacity, *STATE_SHAPE), dtype=np.float32)
        self._actions = np.zeros(capacity, dtype=np.int64)
        self._rewards = np.zeros(capacity, dtype=np.float32)
        self._next_states = np.zeros((capacity, *STATE_SHAPE), dtype=np.float32)
        self._dones = np.zeros(capacity, dtype=np.float32)
        self._next_masks = np.zeros((capacity, COLS), dtype=bool)

        self._write = 0  # o se duoc ghi o lan push tiep theo
        self._size = 0   # so transition dang luu (<= capacity)

    def __len__(self) -> int:
        return self._size

    def __repr__(self) -> str:
        return f"ReplayBuffer(size={self._size}, capacity={self.capacity})"

    def can_sample(self, batch_size: int) -> bool:
        """True neu da du transition de lay mau mot batch."""
        return self._size >= batch_size

    def push(
        self,
        state: np.ndarray,
        action: int,
        reward: float,
        next_state: np.ndarray,
        done: bool,
        next_mask: np.ndarray,
    ) -> None:
        """Them mot transition (s, a, r, s', done, mat na cot hop le cua s').

        Args:
            state: mang (2, 6, 7), thuong la `game.to_array()` truoc khi di.
            action: cot da tha (0..6).
            reward: phan thuong nhan duoc (+1 thang, 0 hoa/chua xong, -1 thua).
            next_state: mang (2, 6, 7) cua ban co khi DQN den luot di tiep
                (tuc sau khi doi thu da dap tra). Khi done=True gia tri nay
                khong duoc dung de tinh muc tieu.
            done: True neu van ket thuc.
            next_mask: mang bool do dai 7, True o cac cot con cho duoc cua
                `next_state`. Tao bang `connect_four.agents.dqn.legal_mask`.

        Raises:
            ValueError: sai shape cua state/next_state/next_mask hoac action ngoai 0..6.
        """
        s = _as_state(state, "state")
        s_next = _as_state(next_state, "next_state")
        col = operator.index(action)
        if not 0 <= col < COLS:
            raise ValueError(f"action phai thuoc 0..{COLS - 1}, nhan duoc {col}.")
        mask = _as_mask(next_mask)

        i = self._write
        self._states[i] = s
        self._actions[i] = col
        self._rewards[i] = reward
        self._next_states[i] = s_next
        self._dones[i] = 1.0 if done else 0.0
        self._next_masks[i] = mask

        self._write = (i + 1) % self.capacity  # het mang thi quay ve 0 -> ghi de cu nhat
        self._size = min(self._size + 1, self.capacity)

    def sample(self, batch_size: int) -> Batch:
        """Lay DUNG `batch_size` transition khac nhau, chon deu ngau nhien.

        Raises:
            ValueError: batch_size <= 0, hoac buffer chua du transition
                (kiem tra truoc bang `can_sample`).
        """
        batch_size = operator.index(batch_size)
        if batch_size <= 0:
            raise ValueError(f"batch_size phai > 0, nhan duoc {batch_size}.")
        if batch_size > self._size:
            raise ValueError(
                f"Buffer moi co {self._size} transition, chua du de lay mau {batch_size}."
            )
        # Chi so 0.._size-1 luon la o da ghi (ca khi buffer chua day lan khi da quay vong).
        idx = self._rng.choice(self._size, size=batch_size, replace=False)
        return Batch(
            states=self._states[idx],
            actions=self._actions[idx],
            rewards=self._rewards[idx],
            next_states=self._next_states[idx],
            dones=self._dones[idx],
            next_masks=self._next_masks[idx],
        )


def _as_state(value: np.ndarray, name: str) -> np.ndarray:
    arr = np.asarray(value, dtype=np.float32)
    if arr.shape != STATE_SHAPE:
        raise ValueError(f"{name} phai co shape {STATE_SHAPE}, nhan duoc {arr.shape}.")
    return arr


def _as_mask(value: np.ndarray) -> np.ndarray:
    arr = np.asarray(value)
    if arr.shape != (COLS,):
        raise ValueError(f"next_mask phai co shape ({COLS},), nhan duoc {arr.shape}.")
    if arr.dtype != np.bool_:
        # Chap nhan mang 0/1, nhung chan danh sach chi so cot nhu [0, 2, 3, ...].
        if not np.isin(arr, (0, 1)).all():
            raise ValueError(
                "next_mask phai la mang bool (True = cot hop le); dung legal_mask(...)."
            )
        arr = arr.astype(bool)
    return arr


# ---------------------------------------------------------------------------
# Lich epsilon (kham pha)
# ---------------------------------------------------------------------------
def epsilon_at(
    episode: int,
    start: float = EPSILON_START,
    decay: float = EPSILON_DECAY,
    floor: float = EPSILON_MIN,
) -> float:
    """Epsilon cua episode thu `episode` (dem tu 0): max(floor, start * decay ** episode).

    Giam theo TUNG EPISODE (khong phai tung buoc), bat dau tu `start` va khong
    bao gio nho hon `floor`.

    Raises:
        ValueError: episode < 0, decay ngoai (0, 1], hoac khong thoa 0 <= floor <= start <= 1.
    """
    _check_schedule(start, decay, floor)
    episode = operator.index(episode)
    if episode < 0:
        raise ValueError(f"episode phai >= 0, nhan duoc {episode}.")
    return float(max(floor, start * decay**episode))


def episodes_to_floor(
    start: float = EPSILON_START,
    decay: float = EPSILON_DECAY,
    floor: float = EPSILON_MIN,
) -> int | None:
    """So episode nho nhat n de epsilon cham san, tuc epsilon_at(n) == floor.

    Dung de chon decay: neu n lon hon so episode huan luyen thi epsilon chua ve
    toi san (vi du decay=0.9998 chua cham san sau 10.000 episode).

    Returns:
        0 neu start == floor; None neu epsilon khong bao gio cham san
        (decay == 1 hoac floor == 0); nguoc lai la so nguyen duong.
    """
    _check_schedule(start, decay, floor)
    if start <= floor:
        return 0
    if decay >= 1.0 or floor <= 0.0:
        return None
    n = max(0, math.ceil(math.log(floor / start) / math.log(decay)))
    # Log co the lech 1 do lam tron so thuc -> dieu chinh theo dung dinh nghia.
    while start * decay**n > floor:
        n += 1
    while n > 0 and start * decay ** (n - 1) <= floor:
        n -= 1
    return n


def _check_schedule(start: float, decay: float, floor: float) -> None:
    if not 0.0 < decay <= 1.0:
        raise ValueError(f"decay phai thuoc (0, 1], nhan duoc {decay!r}.")
    if not 0.0 <= floor <= start <= 1.0:
        raise ValueError(
            f"Can 0 <= floor <= start <= 1, nhan duoc floor={floor!r}, start={start!r}."
        )


# ---------------------------------------------------------------------------
# Vong lap huan luyen (Y3 - chua lam)
# ---------------------------------------------------------------------------
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
    """Huan luyen tac tu DQN cap 6, tra ve duong dan checkpoint tot nhat.

    Args:
        episodes: Tong so episode huan luyen (1.000 pilot -> 10.000 toi da).
        opponent: Loai doi thu tap luyen ('random', 'heuristic', 'alphabeta', 'self_play').
        lr: Toc do hoc cua optimizer (Adam / RMSprop).
        gamma: He so chiet khau phan thuong tuong lai.
        epsilon_start: Gia tri epsilon ban dau cho kham pha.
        epsilon_min: Gia tri epsilon toi thieu.
        epsilon_decay: Ty le giam epsilon sau moi episode / buoc.
        buffer_size: Suc chua toi da cua Replay Buffer.
        batch_size: Kich thuoc batch lay mau tu buffer de update gradient.
        target_update_freq: Tan suat cap nhat trong so sang Target Network.
        checkpoint_milestones: Cac moc episode can luu checkpoint va danh gia.
        out_dir: Thu muc luu checkpoint mo hinh.
        seed: Random seed dam bao kha nang tai lap ket qua.
    """
    raise NotImplementedError(
        "TODO: Cai dat vong lap tuong tac DQN, Replay Buffer, Bellman update va danh gia checkpoint."
    )
