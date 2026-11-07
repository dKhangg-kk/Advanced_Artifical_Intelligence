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

KHUNG - chua co thuat toan day du.
"""

from __future__ import annotations

from pathlib import Path


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
